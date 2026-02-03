from abc import ABC, abstractmethod
import uuid

from app.schema.request.identity.profile import UpdateProfileRequest
from app.schema.response.user import UserResponse


class IProfileService(ABC):
    """Interface for user profile service operations."""

    @abstractmethod
    async def get_profile(self, user_id: uuid.UUID) -> UserResponse:
        """Get current user's profile."""
        pass

    @abstractmethod
    async def update_profile(self, user_id: uuid.UUID, request: UpdateProfileRequest) -> UserResponse:
        """Update user's profile information."""
        pass

    @abstractmethod
    async def change_password(self, user_id: uuid.UUID, current_password: str, new_password: str) -> dict:
        """Change user's password."""
        pass
