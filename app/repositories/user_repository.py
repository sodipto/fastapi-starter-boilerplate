from sqlalchemy import select, func, delete
from sqlalchemy.orm import selectinload
import uuid

from app.models.user import User
from app.models.user_role import UserRole
from app.models.role import Role
from app.repositories.base_repository import BaseRepository
from app.repositories.interfaces.user_repository_interface import IUserRepository


class UserRepository(BaseRepository[User], IUserRepository):
    def __init__(self, db_factory):
        super().__init__(db_factory, User)

    async def get_by_email(self, email: str) -> User | None:
        async with self.db_factory() as session:
            result = await session.execute(
                select(User).where(User.email == email.lower())
            )
            return result.scalars().first()

    async def get_by_email_with_roles(self, email: str) -> User | None:
        query = select(User).options(
            selectinload(User.roles).selectinload(UserRole.role)
        ).where(User.email == email.lower())
        async with self.db_factory() as session:
            result = await session.execute(query)
            return result.scalars().first()

    async def get_by_id_with_roles(self, id: uuid.UUID) -> User | None:
        query = select(User).options(
            selectinload(User.roles).selectinload(UserRole.role)
        ).where(User.id == str(id))
        async with self.db_factory() as session:
            result = await session.execute(query)
            return result.scalars().first()

    async def get_all_paginated(self, skip: int = 0, limit: int = 20, filters: list = None) -> tuple[list[User], int]:
        base_query = select(User)
        if filters:
            for filter_condition in filters:
                base_query = base_query.where(filter_condition)

        count_query = select(func.count()).select_from(base_query.subquery())
        async with self.db_factory() as session:
            total_result = await session.execute(count_query)
            total = total_result.scalar()

            result = await session.execute(
                base_query
                .order_by(User.email)
                .offset(skip)
                .limit(limit)
            )
            users = list(result.scalars().all())

            return users, total

    async def assign_roles(self, user_id: uuid.UUID, role_ids: list[uuid.UUID], auto_commit: bool = True) -> None:
        async with self.db_factory() as session:
            await session.execute(
                delete(UserRole).where(UserRole.user_id == str(user_id))
            )

            for role_id in role_ids:
                user_role = UserRole(
                    user_id=user_id,
                    role_id=role_id
                )
                session.add(user_role)

            if auto_commit:
                await session.commit()
            else:
                await session.flush()
