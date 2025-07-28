from sqlalchemy import select
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Dict
import uuid

from app.models.user import User

class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
        
    async def get_user_by_email(self, email: str) -> User | None:
        result = await self.db.execute(select(User).where(User.Email == email))
        user = result.scalars().first()
        print("User fetched:", user)
        return user
    
    async def get_user_by_id(self, id: uuid.UUID) -> User | None:
        print(f"Fetching user name for id: {id}")
        result = await self.db.execute(select(User).where(User.Id == str(id)))
        user = result.scalars().first()
        print("User fetched:", user)
        return user
