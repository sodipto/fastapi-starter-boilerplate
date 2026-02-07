from abc import ABC, abstractmethod
from typing import TypeVar, Generic, List
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

T = TypeVar('T')


class IBaseRepository(ABC, Generic[T]):
    """Base interface for repository operations."""

    def __init__(self, db: AsyncSession):
        """Initialize repository with database session."""
        pass

    @abstractmethod
    async def create(self, entity: T, auto_commit: bool = True) -> T:
        """Create a new entity."""
        pass

    @abstractmethod
    async def get_by_id(self, id: uuid.UUID) -> T | None:
        """Get entity by id."""
        pass

    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        """Get all entities with pagination."""
        pass

    @abstractmethod
    async def update(self, entity: T, auto_commit: bool = True) -> T:
        """Update an entity."""
        pass

    @abstractmethod
    async def delete(self, id: uuid.UUID, auto_commit: bool = True) -> bool:
        """Delete an entity by id."""
        pass

    @abstractmethod
    async def commit(self) -> None:
        """Commit the current transaction."""
        pass
