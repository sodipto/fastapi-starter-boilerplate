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
    async def get_by_email_with_roles(self, email: str) -> User | None:
        """Get user by email address with roles eagerly loaded."""
        pass

    @abstractmethod
    async def get_by_id_with_roles(self, id: uuid.UUID) -> User | None:
        """Get user by ID with roles eagerly loaded."""
        pass

    @abstractmethod
    async def get_all_paginated(self, skip: int = 0, limit: int = 20, filters: list = None) -> tuple[list[User], int]:
        """Get all users with pagination and total count."""
        pass

    @abstractmethod
    async def assign_roles(self, user_id: uuid.UUID, role_ids: list[uuid.UUID]) -> None:
        """Assign roles to a user, replacing existing roles."""
        pass
