from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.models.user import User
from app.models.user_role import UserRole
from app.repositories.interfaces.user_repository_interface import IUserRepository


class UserRepository(IUserRepository):
    def __init__(self, db: AsyncSession):
        self.db = db
        
    async def get_by_email(self, email: str) -> User | None:
        result = await self.db.execute(select(User).where(User.email == email.lower()))
        user = result.scalars().first()
        return user

    async def get_by_id(self, id: uuid.UUID) -> User | None:
        result = await self.db.execute(select(User).where(User.id == str(id)))
        user = result.scalars().first()
        return user

    async def get_by_id_with_roles(self, id: uuid.UUID) -> User | None:
        query = select(User).options(selectinload(User.roles).selectinload(UserRole.role)).where(User.id == str(id))
        result = await self.db.execute(query)
        user = result.scalars().first()
        return user

    async def update(self, user: User) -> User:
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user
