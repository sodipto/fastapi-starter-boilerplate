from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.models.user import User
from app.models.user_role import UserRole
from app.repositories.base_repository import BaseRepository
from app.repositories.interfaces.user_repository_interface import IUserRepository


class UserRepository(BaseRepository[User], IUserRepository):
    def __init__(self, db: AsyncSession):
        super().__init__(db, User)
        
    async def get_by_email(self, email: str) -> User | None:
        """Get user by email address."""
        result = await self.db.execute(
            select(User).where(User.email == email.lower())
        )
        return result.scalars().first()

    async def get_by_id_with_roles(self, id: uuid.UUID) -> User | None:
        """Get user by ID with roles eagerly loaded."""
        query = select(User).options(
            selectinload(User.roles).selectinload(UserRole.role)
        ).where(User.id == str(id))
        result = await self.db.execute(query)
        return result.scalars().first()
