from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.models.role import Role
from app.repositories.base_repository import BaseRepository
from app.repositories.interfaces.role_repository_interface import IRoleRepository


class RoleRepository(BaseRepository[Role], IRoleRepository):
    def __init__(self, db: AsyncSession):
        super().__init__(db, Role)
        
    async def get_by_name(self, name: str) -> Role | None:
        """Get role by normalized name."""
        normalized_name = name.upper()
        result = await self.db.execute(
            select(Role).where(Role.normalized_name == normalized_name)
        )
        return result.scalars().first()

    async def get_all_paginated(self, skip: int = 0, limit: int = 20) -> tuple[list[Role], int]:
        """Get all roles with pagination and total count."""
        # Get total count
        count_query = select(func.count()).select_from(Role)
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        # Get paginated results
        result = await self.db.execute(
            select(Role).offset(skip).limit(limit)
        )
        roles = list(result.scalars().all())
        
        return roles, total

    async def name_exists(self, name: str, exclude_id: uuid.UUID | None = None) -> bool:
        """Check if role name already exists."""
        normalized_name = name.upper()
        query = select(Role).where(Role.normalized_name == normalized_name)
        
        if exclude_id:
            query = query.where(Role.id != str(exclude_id))
        
        result = await self.db.execute(query)
        return result.scalars().first() is not None
