from typing import TypeVar, Generic, Type, List, Callable
from sqlalchemy import select, delete as sql_delete
import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.interfaces.base_repository_interface import IBaseRepository

T = TypeVar('T')


class BaseRepository(IBaseRepository[T], Generic[T]):
    """Base repository with common CRUD operations.

    This repository accepts a `db_factory` (callable/sessionmaker) which is used
    to create a fresh `AsyncSession` for each operation to ensure connections
    are returned to the pool promptly.
    """

    def __init__(self, db_factory: Callable[[], AsyncSession], model: Type[T]):
        self.db_factory = db_factory
        self.model = model

    async def create(self, entity: T, auto_commit: bool = True) -> T:
        async with self.db_factory() as session:
            session.add(entity)
            if auto_commit:
                await session.commit()
            else:
                await session.flush()
            await session.refresh(entity)
            return entity

    async def get_by_id(self, id: uuid.UUID) -> T | None:
        async with self.db_factory() as session:
            result = await session.execute(
                select(self.model).where(self.model.id == str(id))
            )
            return result.scalars().first()

    async def get_all(self, skip: int = 0, limit: int = 20) -> List[T]:
        async with self.db_factory() as session:
            result = await session.execute(
                select(self.model).order_by(self.model.id).offset(skip).limit(limit)
            )
            return list(result.scalars().all())

    async def update(self, entity: T, auto_commit: bool = True) -> T:
        async with self.db_factory() as session:
            session.add(entity)
            if auto_commit:
                await session.commit()
            else:
                await session.flush()
            await session.refresh(entity)
            return entity

    async def delete(self, id: uuid.UUID, auto_commit: bool = True) -> bool:
        async with self.db_factory() as session:
            # Load the entity first so ORM-level delete is recorded by session
            result = await session.execute(
                select(self.model).where(self.model.id == str(id))
            )
            entity = result.scalars().first()
            if not entity:
                return False
            # Use ORM delete so audit event listeners can capture old values
            await session.delete(entity)
            if auto_commit:
                await session.commit()
            else:
                await session.flush()
            return True

    async def commit(self) -> None:
        async with self.db_factory() as session:
            await session.commit()
