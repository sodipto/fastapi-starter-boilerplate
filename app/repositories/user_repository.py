from sqlalchemy import select
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.models.user import User

class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
        
    async def get_user_by_email(self, email: str) -> User | None:
        result = await self.db.execute(select(User).where(User.Email == email))
        user = result.scalars().first()
        return user
    
    async def get_user_by_id(self, id: uuid.UUID) -> User | None:
        result = await self.db.execute(select(User).where(User.Id == str(id)))
        user = result.scalars().first()
        return user
