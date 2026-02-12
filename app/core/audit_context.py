from __future__ import annotations

from typing import Optional
import contextvars

# Context variable holding the current request's acting user id for auditing.
_current_audit_user: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    "current_audit_user", default=None
)


def set_current_audit_user(user_id: Optional[str] | None) -> None:
    if user_id is None:
        try:
            _current_audit_user.set(None)
        except Exception:
            pass
        return
    try:
        _current_audit_user.set(str(user_id))
    except Exception:
        pass


def get_current_audit_user() -> Optional[str]:
    return _current_audit_user.get()
