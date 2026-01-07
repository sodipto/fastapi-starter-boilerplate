from datetime import datetime, timedelta, timezone
from typing import Tuple, Optional, Dict
from uuid import UUID

from jose import jwt, JWTError

from app.core.config import settings
from app.models.user import User
from app.schema.response.auth import TokenResponse
from app.services.interfaces import ITokenService


class TokenService(ITokenService):
    def __init__(self):
        """Initialize the TokenService with JWT configuration from settings."""
        self.secret_key = settings.SECRET_KEY
        self.algorithm = settings.TOKEN_ALGORITHM
        self.access_token_expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES
        self.refresh_token_expire_days = settings.REFRESH_TOKEN_EXPIRE_DAYS

    def generate_access_token(self, user_id: UUID, email: str) -> Tuple[str, datetime]:
        expiry_time = datetime.now(timezone.utc) + timedelta(
            minutes=self.access_token_expire_minutes
        )

        payload = {
            "user_id": str(user_id),
            "email": email,
            "exp": expiry_time,
            "iat": datetime.now(timezone.utc),
            "type": "access"
        }

        access_token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return access_token, expiry_time

    def generate_refresh_token(self, user_id: UUID) -> Tuple[str, datetime]:
        expiry_time = datetime.now(timezone.utc) + timedelta(
            days=self.refresh_token_expire_days
        )

        payload = {
            "user_id": str(user_id),
            "exp": expiry_time,
            "iat": datetime.now(timezone.utc),
            "type": "refresh"
        }

        refresh_token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return refresh_token, expiry_time

    def create_token_response(self, user: User) -> TokenResponse:
        # Generate access token
        access_token, access_expiry = self.generate_access_token(user.id, user.email)

        # Generate refresh token
        refresh_token, refresh_expiry = self.generate_refresh_token(user.id)

        return TokenResponse(
            type="bearer",
            access_token=access_token,
            access_token_expiry_time=access_expiry,
            refresh_token=refresh_token,
            refresh_token_expiry_time=refresh_expiry
        )

    def get_user_id_from_access_token(self, token: str) -> Optional[UUID]:
        try:
            # Decode without verifying expiration
            payload = jwt.decode(
                token, 
                self.secret_key, 
                algorithms=[self.algorithm],
                options={"verify_exp": False}
            )
            
            # Verify token type
            if payload.get("type") != "access":
                return None
            
            # Extract and return user_id
            user_id_str = payload.get("user_id")
            if not user_id_str:
                return None
            
            return UUID(user_id_str)
        except (JWTError, ValueError):
            return None

    def verify_refresh_token(self, token: str) -> Optional[Dict]:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # Verify token type
            if payload.get("type") != "refresh":
                return None
            
            return payload
        except JWTError:
            return None
