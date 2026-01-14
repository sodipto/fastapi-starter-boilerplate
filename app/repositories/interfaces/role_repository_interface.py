from abc import abstractmethod
import uuid

from app.models.role import Role
from app.repositories.interfaces.base_repository_interface import IBaseRepository


class IRoleRepository(IBaseRepository[Role]):
    """Interface for role repository operations."""

    @abstractmethod
    async def get_by_name(self, name: str) -> Role | None:
        """Get role by normalized name."""
        pass

    @abstractmethod
    async def get_all_paginated(self, skip: int = 0, limit: int = 20, name: str | None = None, is_system: bool | None = None) -> tuple[list[Role], int]:
        """Get all roles with pagination and total count."""
        pass

    @abstractmethod
    async def name_exists(self, name: str, exclude_id: uuid.UUID | None = None) -> bool:
        """Check if role name already exists."""
        pass
