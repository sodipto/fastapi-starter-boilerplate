"""
Permission Repository Interface

Defines the contract for permission data access operations.
"""

from abc import ABC, abstractmethod
from uuid import UUID


class IPermissionRepository(ABC):
    """
    Abstract base class for permission repository implementations.
    
    Handles database operations for fetching user permissions
    from role-based claims (via UserRole -> Role -> RoleClaim).
    """

    @abstractmethod
    async def get_user_permissions(self, user_id: UUID) -> set[str]:
        """
        Get all permissions assigned to a user through their roles.
        
        Query path: user -> user_roles -> roles -> role_claims
        
        Args:
            user_id: The unique identifier of the user
            
        Returns:
            Set of permission strings from role claims
        """
        pass

    @abstractmethod
    async def get_users_by_role(self, role_id: UUID) -> list[UUID]:
        """
        Get all user IDs that have a specific role.
        
        Used for cache invalidation when role permissions change.
        
        Args:
            role_id: The unique identifier of the role
            
        Returns:
            List of user IDs with this role
        """
        pass
