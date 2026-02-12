"""Centralized audit capture using SQLAlchemy session events.

Approach:
- Collect changed/new/deleted instances in `before_flush` and store lightweight
  change payloads in `session.info['audit_entries']`.
- On `after_commit`, write `AuditLog` rows in a new session so audit errors
  do not roll back the main transaction.
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import event, inspect
from sqlalchemy.orm import Session
import asyncio
from sqlalchemy.orm.attributes import get_history

from app.core.config import settings
from app.core.database.session import async_session
from app.models.audit_log import AuditLog
from app.core.logger import get_logger

_logger = get_logger(__name__)


def _is_model_auditable(instance: Any) -> bool:
    # Skip audit for the AuditLog model itself
    return instance.__class__.__name__ != AuditLog.__name__


def _is_sensitive(name: str) -> bool:
    return name.lower() in [f.lower() for f in (settings.AUDIT_SENSITIVE_FIELDS or [])]


def _truncate(value: Any) -> Any:
    try:
        if value is None:
            return None
        s = value.isoformat() if hasattr(value, "isoformat") else value
        # Convert non-serializable types to string
        if not isinstance(s, (str, int, float, bool, list, dict)):
            s = str(s)
        return s
    except Exception:
        return str(value)


def _collect_changes(session):
    if not settings.AUDIT_ENABLED:
        return

    entries = session.info.setdefault("audit_entries", [])

    # Inserts
    for obj in list(session.new):
        if not _is_model_auditable(obj):
            continue
        state = inspect(obj)
        pk = {col.name: _truncate(getattr(obj, col.key, None)) for col in state.mapper.primary_key}
        new_values = {}
        for attr in state.mapper.column_attrs:
            name = attr.key
            if _is_sensitive(name):
                continue
            try:
                val = getattr(obj, name)
                new_values[name] = _truncate(val)
            except Exception:
                continue
        entries.append(
            {
                "type": "Insert",
                "table": state.mapper.local_table.name,
                "primary_key": pk,
                "old": None,
                "new": new_values,
                "columns": list(new_values.keys()),
            }
        )

    # Updates
    for obj in list(session.dirty):
        if not _is_model_auditable(obj):
            continue
        state = inspect(obj)
        # Skip if no attribute-level changes
        changed = {}
        old_values = {}
        new_values = {}
        cols = []
        for attr in state.mapper.column_attrs:
            name = attr.key
            hist = get_history(obj, name)
            if not hist.has_changes():
                continue
            if _is_sensitive(name):
                continue
            old = hist.deleted[0] if hist.deleted else None
            new = hist.added[0] if hist.added else getattr(obj, name, None)
            old_values[name] = _truncate(old)
            new_values[name] = _truncate(new)
            cols.append(name)
        if cols:
            pk = {col.name: _truncate(getattr(obj, col.key, None)) for col in state.mapper.primary_key}
            entries.append(
                {
                    "type": "Update",
                    "table": state.mapper.local_table.name,
                    "primary_key": pk,
                    "old": old_values,
                    "new": new_values,
                    "columns": cols,
                }
            )

    # Deletes
    for obj in list(session.deleted):
        if not _is_model_auditable(obj):
            continue
        state = inspect(obj)
        pk = {col.name: _truncate(getattr(obj, col.key, None)) for col in state.mapper.primary_key}
        old_values = {}
        for attr in state.mapper.column_attrs:
            name = attr.key
            if _is_sensitive(name):
                continue
            try:
                val = getattr(obj, name)
                old_values[name] = _truncate(val)
            except Exception:
                continue
        entries.append(
            {
                "type": "Delete",
                "table": state.mapper.local_table.name,
                "primary_key": pk,
                "old": old_values,
                "new": None,
                "columns": list(old_values.keys()),
            }
        )


@event.listens_for(Session, "before_flush")
def before_flush(session, flush_context, instances):
    try:
        _collect_changes(session)
    except Exception as ex:
        _logger.error(f"Error collecting audit changes: {ex}")


@event.listens_for(Session, "after_commit")
def after_commit(session):
    if not settings.AUDIT_ENABLED:
        return
    entries = session.info.pop("audit_entries", []) if session.info.get("audit_entries") else []
    if not entries:
        return

    user_id = session.info.get("user_id")

    async def _persist_entries(entries, user_id):
        try:
            async with async_session() as s:
                for e in entries:
                    try:
                        audit = AuditLog(
                            user_id=user_id,
                            type=e.get("type"),
                            table_name=e.get("table"),
                            old_values=e.get("old"),
                            new_values=e.get("new"),
                            affected_columns=e.get("columns"),
                            primary_key=e.get("primary_key"),
                        )
                        s.add(audit)
                    except Exception as ex:
                        _logger.error(f"Failed to build AuditLog object for entry {e}: {ex}")
                try:
                    await s.commit()
                except Exception as ex:
                    _logger.error(f"Failed to persist audit entries: {ex}")
        except Exception as ex:
            _logger.error(f"Unexpected error when saving audit entries: {ex}")

    try:
        # Schedule background task to persist audit entries without blocking the caller
        asyncio.create_task(_persist_entries(entries, user_id))
    except RuntimeError:
        # If there's no running event loop, run synchronously as a fallback
        import asyncio as _asyncio

        loop = _asyncio.new_event_loop()
        try:
            loop.run_until_complete(_persist_entries(entries, user_id))
        finally:
            loop.close()


def set_session_user(session, user_id: str | None) -> None:
    """Convenience helper to attach the acting user id to the SQLAlchemy session.

    Call this from repository/service code when a session is available so audit
    entries can capture `user_id`.
    """
    try:
        if user_id is None:
            return
        session.info["user_id"] = str(user_id)
    except Exception:
        _logger.debug("Failed to set session user for auditing")
