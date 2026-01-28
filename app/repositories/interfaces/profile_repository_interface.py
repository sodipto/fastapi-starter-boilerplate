from abc import ABC, abstractmethod
from app.models.user import User


class IProfileRepository(ABC):
    """Interface for profile repository operations."""

    @abstractmethod
    async def get_user_by_id(self, user_id: int) -> User | None:
        """Get user by ID."""
        pass

    @abstractmethod
    async def get_user_by_email(self, email: str) -> User | None:
        """Get user by email address."""
        pass

    @abstractmethod
    async def update_user(self, user: User) -> User:
        """Update user information."""
        pass
