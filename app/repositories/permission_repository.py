"""
Permission Repository Implementation

Handles database operations for loading user permissions
from role-based claims (via UserRole -> Role -> RoleClaim).

Uses optimized SQL queries with JOINs for performance.
"""

from uuid import UUID
from sqlalchemy import select

from app.core.rbac import PermissionClaimType
from app.models.role_claim import RoleClaim
from app.models.user_role import UserRole
from app.repositories.interfaces.permission_repository_interface import IPermissionRepository


class PermissionRepository(IPermissionRepository):
    """
    SQLAlchemy implementation of the permission repository.
    """

    def __init__(self, db_factory):
        self.db_factory = db_factory

    async def get_user_permissions(self, user_id: UUID) -> set[str]:
        """
        Get all permissions for a user through their assigned roles.
        
        Query path: user_roles -> roles -> role_claims
        Filters by claim_type = 'permission'
        
        Args:
            user_id: UUID of the user
            
        Returns:
            Set of permission strings from role claims
        """
        # Query to get all role claims for user's roles
        # This performs: user_roles JOIN role_claims WHERE claim_type = 'permission'
        query = (
            select(RoleClaim.claim_name)
            .join(UserRole, UserRole.role_id == RoleClaim.role_id)
            .where(
                UserRole.user_id == user_id,
                RoleClaim.claim_type == PermissionClaimType.PERMISSION.value
            )
            .distinct()  # Avoid duplicates if user has multiple roles with same permission
        )
        
        async with self.db_factory() as session:
            result = await session.execute(query)
            return set(result.scalars().all())

    async def get_users_by_role(self, role_id: UUID) -> list[UUID]:
        """
        Get all user IDs that have a specific role.
        
        Used for bulk cache invalidation when role permissions change.
        
        Args:
            role_id: UUID of the role
            
        Returns:
            List of user UUIDs with this role
        """
        query = (
            select(UserRole.user_id)
            .where(UserRole.role_id == role_id)
        )
        
        async with self.db_factory() as session:
            result = await session.execute(query)
            return list(result.scalars().all())
