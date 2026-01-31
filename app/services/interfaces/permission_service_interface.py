"""
RBAC Permission Service Interface

Defines the contract for permission-related operations
in the Role-Based Access Control system.
"""

from abc import ABC, abstractmethod
from uuid import UUID


class IPermissionService(ABC):
    """
    Abstract base class for permission service implementations.
    
    This service handles all permission-related operations including:
    - Loading user permissions from roles (via UserRole -> Role -> RoleClaim)
    - Checking if a user has specific permissions
    - Caching permissions for performance
    """

    @abstractmethod
    async def get_user_permissions(self, user_id: UUID) -> set[str]:
        """
        Get all permissions for a user through their assigned roles.
        
        Permission flow: user -> user_roles -> roles -> role_claims
        
        Args:
            user_id: The unique identifier of the user
            
        Returns:
            Set of permission strings the user has
        """
        pass

    @abstractmethod
    async def has_permission(self, user_id: UUID, permission: str) -> bool:
        """
        Check if a user has a specific permission.
        
        Args:
            user_id: The unique identifier of the user
            permission: The permission string to check
            
        Returns:
            True if user has the permission, False otherwise
        """
        pass

    @abstractmethod
    async def has_any_permission(self, user_id: UUID, permissions: list[str]) -> bool:
        """
        Check if a user has any of the specified permissions (OR logic).
        
        Args:
            user_id: The unique identifier of the user
            permissions: List of permission strings to check
            
        Returns:
            True if user has at least one permission, False otherwise
        """
        pass

    @abstractmethod
    async def has_all_permissions(self, user_id: UUID, permissions: list[str]) -> bool:
        """
        Check if a user has all specified permissions (AND logic).
        
        Args:
            user_id: The unique identifier of the user
            permissions: List of permission strings to check
            
        Returns:
            True if user has all permissions, False otherwise
        """
        pass

    @abstractmethod
    async def invalidate_user_permissions_cache(self, user_id: UUID) -> None:
        """
        Invalidate cached permissions for a user.
        
        Should be called when:
        - User roles are modified
        - Role permissions are modified
        
        Args:
            user_id: The unique identifier of the user
        """
        pass

    @abstractmethod
    async def invalidate_role_permissions_cache(self, role_id: UUID) -> None:
        """
        Invalidate cached permissions for all users with a specific role.
        
        Should be called when role permissions are modified.
        
        Args:
            role_id: The unique identifier of the role
        """
        pass
