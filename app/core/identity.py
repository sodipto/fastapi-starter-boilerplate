from uuid import UUID
from fastapi import Request
from app.utils.exception_utils import UnauthorizedException
from app.core.config import settings
from app.utils.auth_utils import ALGORITHM
from jose import JWTError, jwt


def get_current_user_id(request: Request) -> UUID:
        """Return the current user's UUID.

        Flow:
        - Prefer reading a cached decoded payload placed on `request.state` by
            `JWTBearer`.
        - If missing, fall back to `extract_user_id_from_request` which decodes the
            Authorization header. The `default_user_id` used here is the nil UUID
            string so callers that want an empty UUID get it instead of the
            literal 'Anonymous'.
        """
        user_id = extract_user_id_from_request(request, default_user_id=str(UUID(int=0)))
        try:
                return UUID(user_id)
        except Exception:
                raise UnauthorizedException("Could not validate credentials!")


def extract_user_id_from_request(request: Request, default_user_id: str = "Anonymous") -> str:
    """Return the user_id stored in the Authorization header, or `default_user_id`.

    The `default_user_id` parameter lets callers request an alternative return
    value (for example an empty string or a nil UUID string) when no valid
    user id is present in the request.
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return default_user_id
    token = auth_header.split(" ", 1)[1]
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=ALGORITHM)
    except (JWTError, ValueError):
        return default_user_id
    user_id = payload.get("user_id")
    if isinstance(user_id, str):
        try:
            user_id = UUID(user_id)
        except Exception:
            return default_user_id
    return str(user_id) if user_id else default_user_id