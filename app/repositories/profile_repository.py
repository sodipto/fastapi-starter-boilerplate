from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.base_repository import BaseRepository
from app.repositories.interfaces.profile_repository_interface import IProfileRepository


class ProfileRepository(BaseRepository[User], IProfileRepository):
    """Repository for profile-related database operations."""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, User)
        
    async def get_user_by_id(self, user_id: int) -> User | None:
        """Get user by ID."""
        result = await self.db.execute(
            select(User).where(User.id == str(user_id))
        )
        return result.scalars().first()

    async def get_user_by_email(self, email: str) -> User | None:
        """Get user by email address."""
        result = await self.db.execute(
            select(User).where(User.email == email.lower())
        )
        return result.scalars().first()

    async def update_user(self, user: User) -> User:
        """Update user information."""
        return await self.update(user)
