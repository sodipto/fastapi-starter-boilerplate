from abc import ABC, abstractmethod
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.models.user import User


class IUserRepository(ABC):
    """Interface for user repository operations."""

    def __init__(self, db: AsyncSession):
        """Initialize repository with database session."""
        pass

    @abstractmethod
    async def get_by_email(self, email: str) -> User | None:
        """Get user by email address."""
        pass

    @abstractmethod
    async def get_by_id(self, id: uuid.UUID) -> User | None:
        """Get user by ID."""
        pass

    @abstractmethod
    async def get_by_id_with_roles(self, id: uuid.UUID) -> User | None:
        """Get user by ID with roles eagerly loaded."""
        pass

    @abstractmethod
    async def update(self, user: User) -> User:
        """Update user in database."""
        pass
