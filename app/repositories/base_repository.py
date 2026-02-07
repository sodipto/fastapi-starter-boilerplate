from typing import TypeVar, Generic, Type, List
from sqlalchemy import select, delete as sql_delete
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.repositories.interfaces.base_repository_interface import IBaseRepository

T = TypeVar('T')


class BaseRepository(IBaseRepository[T], Generic[T]):
    """Base repository with common CRUD operations."""

    def __init__(self, db: AsyncSession, model: Type[T]):
        self.db = db
        self.model = model

    async def create(self, entity: T, auto_commit: bool = True) -> T:
        """Create a new entity in the database."""
        self.db.add(entity)
        if auto_commit:
            await self.db.commit()
        else:
            await self.db.flush()
        await self.db.refresh(entity)

        return entity

    async def get_by_id(self, id: uuid.UUID) -> T | None:
        """Get entity by id."""
        result = await self.db.execute(
            select(self.model).where(self.model.id == str(id))
        )

        return result.scalars().first()

    async def get_all(self, skip: int = 0, limit: int = 20) -> List[T]:
        """Get all entities with pagination."""
        result = await self.db.execute(
            select(self.model).order_by(self.model.id).offset(skip).limit(limit)
        )

        return list(result.scalars().all())

    async def update(self, entity: T, auto_commit: bool = True) -> T:
        """Update an entity in the database."""
        self.db.add(entity)
        if auto_commit:
            await self.db.commit()
        else:
            await self.db.flush()
        await self.db.refresh(entity)

        return entity

    async def delete(self, id: uuid.UUID, auto_commit: bool = True) -> bool:
        """Delete an entity by id."""
        result = await self.db.execute(
            sql_delete(self.model).where(self.model.id == str(id))
        )
        if auto_commit:
            await self.db.commit()
        else:
            await self.db.flush()

        return result.rowcount > 0

    async def commit(self) -> None:
        """Commit the current transaction."""
        await self.db.commit()
