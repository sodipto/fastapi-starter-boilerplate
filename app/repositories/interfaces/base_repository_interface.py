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
    async def create(self, entity: T) -> T:
        """Create a new entity."""
        pass

    @abstractmethod
    async def get_by_id(self, id: uuid.UUID) -> T | None:
        """Get entity by ID."""
        pass

    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        """Get all entities with pagination."""
        pass

    @abstractmethod
    async def update(self, entity: T) -> T:
        """Update an entity."""
        pass

    @abstractmethod
    async def delete(self, id: uuid.UUID) -> bool:
        """Delete an entity by ID."""
        pass

    @abstractmethod
    async def exists(self, id: uuid.UUID) -> bool:
        """Check if entity exists by ID."""
        pass
