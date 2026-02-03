from abc import ABC, abstractmethod
import uuid

from app.schema.response.user import UserResponse


class IProfileService(ABC):
    """Interface for user profile service operations."""

    @abstractmethod
    async def get_profile(self, user_id: uuid.UUID) -> UserResponse:
        """Get current user's profile."""
        pass

    @abstractmethod
    async def update_profile(self, user_id: uuid.UUID, full_name: str, email: str) -> UserResponse:
        """Update user's profile information."""
        pass

    @abstractmethod
    async def change_password(self, user_id: uuid.UUID, current_password: str, new_password: str) -> dict:
        """Change user's password."""
        pass
