from uuid import UUID
from fastapi import HTTPException, Request
from app.core.config import settings
from app.utils.auth_utils import ALGORITHM
from jose import JWTError, jwt


def get_current_user(request: Request) -> UUID:
    """Return the current user's UUID.

    Flow:
    - If missing, fall back to `extract_user_id_from_request(request)` which decodes
      the Authorization header.
    """
    return extract_user_id_from_request(request,fallback=UUID(int=0))


def extract_user_id_from_request(request: Request, fallback: str = "Anonymous") -> str:
    """Return the user_id stored in the Authorization header, or `fallback`.

    The `fallback` parameter lets callers request an alternative return
    value (for example an empty string or a nil UUID string) when no valid
    user id is present in the request.
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return fallback
    token = auth_header.split(" ", 1)[1]
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=ALGORITHM)
    except (JWTError, ValueError):
        return fallback
    user_id = payload.get("user_id")
    if isinstance(user_id, str):
        try:
            user_id = UUID(user_id)
        except Exception:
            return fallback
    return str(user_id) if user_id else fallback