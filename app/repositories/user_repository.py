from sqlalchemy import select, func, delete
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.models.user import User
from app.models.user_role import UserRole
from app.models.role import Role
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

    async def get_by_email_with_roles(self, email: str) -> User | None:
        """Get user by email address with roles eagerly loaded."""
        query = select(User).options(
            selectinload(User.roles).selectinload(UserRole.role)
        ).where(User.email == email.lower())
        result = await self.db.execute(query)
        user = result.scalars().first()

        for user_role in user.roles or []:
            print(f"User Role: {user_role.role.name}")
        
        # Map UserRole objects to role objects for easier access
        # if user and user.roles:
        #     user.roles = [ur.role for ur in user.roles if ur.role]
        # else:
        #     user.roles = [] if user else None
            
        return user

    async def get_by_id_with_roles(self, id: uuid.UUID) -> User | None:
        """Get user by ID with roles eagerly loaded."""
        query = select(User).options(
            selectinload(User.roles).selectinload(UserRole.role)
        ).where(User.id == str(id))
        result = await self.db.execute(query)
        user = result.scalars().first()
        
        # # Map UserRole objects to role objects for easier access
        # if user and user.roles:
        #     user.roles = [ur.role for ur in user.roles if ur.role]
        # else:
        #     user.roles = [] if user else None
            
        return user

    async def get_all_paginated(self, skip: int = 0, limit: int = 20, filters: list = None) -> tuple[list[User], int]:
        """Get all users with pagination and total count."""
        # Build base query with optional filters
        base_query = select(User)
        if filters:
            for filter_condition in filters:
                base_query = base_query.where(filter_condition)
        
        # Get total count
        count_query = select(func.count()).select_from(base_query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        # Get paginated results
        result = await self.db.execute(
            base_query
            .order_by(User.email)
            .offset(skip)
            .limit(limit)
        )
        users = list(result.scalars().all())
        
        return users, total

    async def assign_roles(self, user_id: uuid.UUID, role_ids: list[uuid.UUID]) -> None:
        """Assign roles to a user, replacing existing roles."""
        # Remove existing user roles
        await self.db.execute(
            delete(UserRole).where(UserRole.user_id == str(user_id))
        )
        
        # Add new user roles
        for role_id in role_ids:
            user_role = UserRole(
                user_id=user_id,
                role_id=role_id
            )
            self.db.add(user_role)
        
        # Flush to persist changes
        await self.db.flush()
