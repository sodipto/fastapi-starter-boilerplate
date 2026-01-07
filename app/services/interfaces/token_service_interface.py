from abc import ABC, abstractmethod
from datetime import datetime
from typing import Tuple, Optional, Dict
from uuid import UUID

from app.models.user import User
from app.schema.response.auth import TokenResponse


class ITokenService(ABC):
    """Interface for token service operations."""

    @abstractmethod
    def generate_access_token(self, user_id: UUID, email: str) -> Tuple[str, datetime]:
        """Generate an access token for the given user."""
        pass

    @abstractmethod
    def generate_refresh_token(self, user_id: UUID) -> Tuple[str, datetime]:
        """Generate a refresh token for the given user."""
        pass

    @abstractmethod
    def create_token_response(self, user: User) -> TokenResponse:
        """Create a token response with both access and refresh tokens."""
        pass

    @abstractmethod
    def get_user_id_from_access_token(self, token: str) -> Optional[UUID]:
        """Extract user ID from an access token."""
        pass

    @abstractmethod
    def verify_refresh_token(self, token: str) -> Optional[Dict]:
        """Verify a refresh token and return its payload."""
        pass
