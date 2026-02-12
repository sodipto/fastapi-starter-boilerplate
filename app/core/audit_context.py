from __future__ import annotations

from typing import Optional
import contextvars
import uuid

# Context variable holding the current request's acting user id for auditing.
# Store `uuid.UUID` objects (or `None`) so consumers always receive a typed UUID.
_current_audit_user: contextvars.ContextVar[Optional[uuid.UUID]] = contextvars.ContextVar(
    "current_audit_user", default=None
)


def set_current_audit_user(user_id: Optional[str] = None) -> None:
    """Set the current audit user in the contextvar.

    Accepts a string (UUID string) or `None`. The function converts the
    provided string to a `uuid.UUID` and stores that; invalid strings clear
    the context to avoid propagating bad values.
    """
    if user_id is None:
        try:
            _current_audit_user.set(None)
        except Exception:
            pass
        return

    try:
        _current_audit_user.set(uuid.UUID(str(user_id)))
    except Exception:
        try:
            _current_audit_user.set(None)
        except Exception:
            pass


def get_current_audit_user() -> Optional[uuid.UUID]:
    """Return the current audit user as a `uuid.UUID` or `None`."""
    return _current_audit_user.get()
