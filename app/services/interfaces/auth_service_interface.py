from abc import ABC, abstractmethod
import uuid

from app.schema.response.auth import AuthResponse


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
