from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
import uuid

from app.core.rbac import PermissionClaimType
from app.models.role import Role
from app.models.role_claim import RoleClaim
from app.models.user_role import UserRole
from app.repositories.base_repository import BaseRepository
from app.repositories.interfaces.role_repository_interface import IRoleRepository


class RoleRepository(BaseRepository[Role], IRoleRepository):
    def __init__(self, db: AsyncSession):
        super().__init__(db, Role)
        
    async def get_by_id(self, id: uuid.UUID) -> Role | None:
        """Get role by id with claims loaded."""
        result = await self.db.execute(
            select(Role)
            .options(selectinload(Role.role_claims))
            .where(Role.id == str(id))
        )
        return result.scalars().first()

    async def get_by_ids(self, ids: list[uuid.UUID]) -> list[Role]:
        """Get multiple roles by ids."""
        if not ids:
            return []
        
        str_ids = [str(id) for id in ids]
        result = await self.db.execute(
            select(Role).where(Role.id.in_(str_ids))
        )
        return list(result.scalars().all())
        
    async def get_by_normalized_name(self, name: str) -> Role | None:
        """Get role by normalized name."""
        normalized_name = name.upper()
        result = await self.db.execute(
            select(Role)
            .options(selectinload(Role.role_claims))
            .where(Role.normalized_name == normalized_name)
        )
        return result.scalars().first()

    async def get_all_paginated(self, skip: int = 0, limit: int = 20, name: str | None = None, is_system: bool | None = None) -> tuple[list[Role], int]:
        """Get all roles with pagination and total count."""
        # Build base query with optional filters
        base_query = select(Role)
        if name is not None:
            base_query = base_query.where(Role.name.ilike(f"%{name}%"))
        if is_system is not None:
            base_query = base_query.where(Role.is_system == is_system)
        
        # Get total count
        count_query = select(func.count()).select_from(base_query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        # Get paginated results with claims
        result = await self.db.execute(
            base_query
            .options(selectinload(Role.role_claims))
            .order_by(Role.name)
            .offset(skip)
            .limit(limit)
        )
        roles = list(result.scalars().all())
        
        return roles, total

    async def name_exists(self, name: str, exclude_id: uuid.UUID | None = None) -> bool:
        """Check if role name already exists."""
        query = select(Role).where(func.lower(Role.name) == name.lower())
        
        if exclude_id:
            query = query.where(Role.id != str(exclude_id))
        
        result = await self.db.execute(query)
        return result.scalars().first() is not None

    async def get_role_claims(self, role_id: uuid.UUID) -> list[RoleClaim]:
        """Get all claims for a role."""
        result = await self.db.execute(
            select(RoleClaim).where(
                RoleClaim.role_id == str(role_id),
                RoleClaim.claim_type == PermissionClaimType.PERMISSION.value
            )
        )
        return list(result.scalars().all())

    async def sync_role_claims(self, role_id: uuid.UUID, claim_names: list[str], auto_commit: bool = True) -> list[RoleClaim]:
        """
        Sync role claims - add new, remove old, keep existing.
        
        Args:
            role_id: The role ID
            claim_names: List of claim names that should exist
            auto_commit: Whether to commit changes
            
        Returns:
            List of current claims after sync
        """
        # Get existing claims
        result = await self.db.execute(
            select(RoleClaim.claim_name).where(
                RoleClaim.role_id == str(role_id),
                RoleClaim.claim_type == PermissionClaimType.PERMISSION.value
            )
        )
        existing_claim_names = set(result.scalars().all())
        target_claim_names = set(claim_names)
        
        # Claims to add (new ones)
        claims_to_add = target_claim_names - existing_claim_names
        
        # Claims to remove (no longer needed)
        claims_to_remove = existing_claim_names - target_claim_names
        
        # Remove old claims
        if claims_to_remove:
            await self.db.execute(
                delete(RoleClaim).where(
                    RoleClaim.role_id == str(role_id),
                    RoleClaim.claim_name.in_(claims_to_remove),
                    RoleClaim.claim_type == PermissionClaimType.PERMISSION.value
                )
            )
        
        # Add new claims
        for claim_name in claims_to_add:
            new_claim = RoleClaim(
                role_id=role_id,
                claim_type=PermissionClaimType.PERMISSION.value,
                claim_name=claim_name
            )
            self.db.add(new_claim)
        
        # Flush or commit
        if auto_commit:
            await self.db.commit()
        else:
            await self.db.flush()
        
        # Return updated claims
        return await self.get_role_claims(role_id)

    async def has_users(self, role_id: uuid.UUID) -> tuple[bool, int]:
        """Check if role is assigned to any users.
        
        Returns:
            Tuple of (has_users, user_count)
        """
        result = await self.db.execute(
            select(func.count()).select_from(UserRole).where(
                UserRole.role_id == str(role_id)
            )
        )
        count = result.scalar()
        return count > 0, count
