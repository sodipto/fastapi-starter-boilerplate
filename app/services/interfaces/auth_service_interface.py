from abc import ABC, abstractmethod
import uuid

from app.schema.response.auth import AuthResponse
from app.schema.response.meta import ResponseMeta


class IAuthService(ABC):
    """Interface for authentication service operations."""

    @abstractmethod
    async def login(self, email: str, password: str) -> AuthResponse:
        """Authenticate user with email and password."""
        pass

    @abstractmethod
    async def refresh_token(self, access_token: str, refresh_token: str) -> AuthResponse:
        """Refresh access token using refresh token."""
        pass

    @abstractmethod
    async def forgot_password(self, email: str) -> ResponseMeta:
        """Send password reset verification code to user's email."""
        pass

    @abstractmethod
    async def reset_password(self, email: str, verification_code: str, new_password: str) -> ResponseMeta:
        """Reset user password using verification code."""
        pass
