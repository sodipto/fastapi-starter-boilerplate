from abc import ABC, abstractmethod
from datetime import datetime, timedelta, timezone
from typing import Tuple, Optional, Dict
from uuid import UUID

from jose import jwt, JWTError

from app.core.config import settings
from app.models.user import User
from app.schema.response.auth import TokenResponse


class ITokenService(ABC):
    @abstractmethod
    def generate_access_token(self, user_id: UUID, email: str) -> Tuple[str, datetime]:
        """
        Generate a JWT access token for a user.

        Args:
            user_id: The unique identifier of the user
            email: The email address of the user

        Returns:
            A tuple containing (access_token, expiry_datetime)
        """
        pass

    @abstractmethod
    def generate_refresh_token(self, user_id: UUID) -> Tuple[str, datetime]:
        """
        Generate a secure refresh token for a user.

        Args:
            user_id: The unique identifier of the user

        Returns:
            A tuple containing (refresh_token, expiry_datetime)
        """
        pass

    @abstractmethod
    def create_token_response(self, user: User) -> TokenResponse:
        """
        Create a complete token response including access and refresh tokens.

        Args:
            user: The User model instance

        Returns:
            TokenResponse containing access and refresh tokens with expiry times
        """
        pass

    @abstractmethod
    def get_user_id_from_access_token(self, token: str) -> Optional[UUID]:
        """
        Extract user ID from an access token without verifying expiration.

        Args:
            token: The JWT access token

        Returns:
            User UUID if token is valid, None otherwise
        """
        pass

    @abstractmethod
    def verify_refresh_token(self, token: str) -> Optional[Dict]:
        """
        Verify and decode a refresh token.

        Args:
            token: The JWT refresh token to verify

        Returns:
            Decoded token payload if valid, None otherwise
        """
        pass


class TokenService(ITokenService):
    """
    Concrete implementation of ITokenService for JWT token generation and management.
    
    This service handles:
    - JWT access token generation with short expiration (15 minutes)
    - JWT refresh token generation with longer expiration (7 days)
    - Token response creation with database persistence
    """

    def __init__(self):
        """Initialize the TokenService with JWT configuration from settings."""
        self.secret_key = settings.SECRET_KEY
        self.algorithm = settings.TOKEN_ALGORITHM
        self.access_token_expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES
        self.refresh_token_expire_days = settings.REFRESH_TOKEN_EXPIRE_DAYS

    def generate_access_token(self, user_id: UUID, email: str) -> Tuple[str, datetime]:
        """
        Generate a JWT access token with user claims.

        Args:
            user_id: The unique identifier of the user
            email: The email address of the user

        Returns:
            A tuple containing (access_token, expiry_datetime)
        """
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
        """
        Generate a JWT refresh token.

        Args:
            user_id: The unique identifier of the user

        Returns:
            A tuple containing (refresh_token, expiry_datetime)
        """
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
        """
        Create a complete token response with access and refresh tokens.

        Args:
            user: The User model instance

        Returns:
            TokenResponse containing both access and refresh tokens with expiry times
        """
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
        """
        Extract user ID from an access token without verifying expiration.

        Args:
            token: The JWT access token

        Returns:
            User UUID if token is valid, None otherwise
        """
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
        """
        Verify and decode a refresh token.

        Args:
            token: The JWT refresh token to verify

        Returns:
            Decoded token payload if valid, None otherwise
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # Verify token type
            if payload.get("type") != "refresh":
                return None
            
            return payload
        except JWTError:
            return None
