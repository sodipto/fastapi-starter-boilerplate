from datetime import datetime
from datetime import timezone
from fastapi import Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.core.config import settings
from jose import jwt

from app.utils.auth_utils import ALGORITHM
from app.utils.exception_utils import UnauthorizedException
from app.core.audit_context import set_current_audit_user

def decode_jwt(token: str) -> dict:
    try:
        decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=ALGORITHM)
        return decoded_token if decoded_token["exp"] >= int(datetime.now(timezone.utc).timestamp()) else None
    except Exception:
        return {}
    
class JWTBearer(HTTPBearer):
    def __init__(self):
        super(JWTBearer, self).__init__(auto_error=False)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
        if credentials:
            if  credentials.scheme != "Bearer":
                raise UnauthorizedException("Invalid authentication scheme!")
            if not self.verify_jwt(credentials.credentials):
                raise UnauthorizedException("Invalid or expired token!")
            # set current audit user in context so DB sessions can pick it up
            try:
                payload = decode_jwt(credentials.credentials)
                user_id = payload.get("user_id") if isinstance(payload, dict) else None
                if user_id:
                    set_current_audit_user(str(user_id))
            except Exception:
                # don't block authentication flow on audit context errors
                pass
            return credentials.credentials
        else:
            raise UnauthorizedException("Invalid or expired token!")

    def verify_jwt(self, jwt_token: str) -> bool:
        is_token_valid: bool = False
        try:
            payload = decode_jwt(jwt_token)
        except Exception as e:
            payload = None
        if payload:
            is_token_valid = True
        return is_token_valid