from abc import ABC, abstractmethod
import uuid

from app.schema.response.user import UserResponse


class IUserService(ABC):
    """Interface for user service operations."""

    @abstractmethod
    async def get_by_id(self, user_id: uuid.UUID) -> UserResponse:
        """Get user by ID."""
        pass
