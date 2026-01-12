from abc import abstractmethod
import uuid

from app.models.user import User
from app.repositories.interfaces.base_repository_interface import IBaseRepository


class IUserRepository(IBaseRepository[User]):
    """Interface for user repository operations."""

    @abstractmethod
    async def get_by_email(self, email: str) -> User | None:
        """Get user by email address."""
        pass

    @abstractmethod
    async def get_by_id_with_roles(self, id: uuid.UUID) -> User | None:
        """Get user by ID with roles eagerly loaded."""
        pass
