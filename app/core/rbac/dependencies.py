"""
RBAC Permission Dependencies

This module provides FastAPI dependency injection functions for
permission-based authorization. It implements a clean, reusable
pattern for protecting endpoints with permission checks.

Features:
- Single permission checks
- Multiple permission checks (OR logic)
- Multiple permission checks (AND logic)
- Integration with JWT authentication
- Performance-optimized with caching

Usage Examples:
    from app.core.rbac import Permission, require_permission
    
    # Single permission
    @router.get("/users", dependencies=[Depends(require_permission(Permission.USERS_VIEW))])
    
    # Multiple permissions (OR - any one is sufficient)
    @router.get("/reports", dependencies=[Depends(require_any_permission(
        Permission.REPORTS_VIEW, Permission.ADMIN_ACCESS
    ))])
    
    # Multiple permissions (AND - all required)
    @router.delete("/users/{id}", dependencies=[Depends(require_all_permissions(
        Permission.USERS_DELETE, Permission.AUDIT_VIEW
    ))])
"""

from typing import Callable
from uuid import UUID
from fastapi import Depends, HTTPException, status

from app.core.identity import get_current_user
from app.core.rbac.permissions import Permission
from app.core.container import Container
from app.services.interfaces.permission_service_interface import IPermissionService
from dependency_injector.wiring import inject, Provide


class PermissionChecker:
    """
    Permission checker class for FastAPI dependency injection.
    
    This class is instantiated with required permission(s) and
    used as a callable dependency in route definitions.
    
    Attributes:
        required_permissions: List of permission strings to check
        require_all: If True, all permissions are required (AND logic)
                    If False, any permission is sufficient (OR logic)
    """

    def __init__(
        self,
        permissions: list[Permission],
        require_all: bool = False
    ):
        """
        Initialize the permission checker.
        
        Args:
            permissions: List of Permission enum values to check
            require_all: Whether all permissions are required (default: False)
        """
        # Convert Permission enums to string values
        self.required_permissions = [p.value for p in permissions]
        self.require_all = require_all

    @inject
    async def __call__(
        self,
        user_id: UUID = Depends(get_current_user),
        permission_service: IPermissionService = Depends(
            Provide[Container.permission_service]
        )
    ) -> UUID:
        """
        Check if the current user has the required permission(s).
        
        This method is called by FastAPI's dependency injection system
        when the route is accessed.
        
        Args:
            user_id: Current user's ID from JWT token
            permission_service: Injected permission service
            
        Returns:
            The user_id if permission check passes
            
        Raises:
            HTTPException 403: If permission check fails
        """
        # Perform permission check based on mode (AND/OR)
        if self.require_all:
            # AND logic - user must have ALL permissions
            has_permission = await permission_service.has_all_permissions(
                user_id, 
                self.required_permissions
            )
        else:
            # OR logic - user needs at least ONE permission
            if len(self.required_permissions) == 1:
                # Single permission check (optimized path)
                has_permission = await permission_service.has_permission(
                    user_id, 
                    self.required_permissions[0]
                )
            else:
                # Multiple permissions with OR logic
                has_permission = await permission_service.has_any_permission(
                    user_id, 
                    self.required_permissions
                )

        if not has_permission:
            # Build informative error message
            if len(self.required_permissions) == 1:
                detail = f"Permission denied. Required: {self.required_permissions[0]}"
            elif self.require_all:
                detail = f"Permission denied. Required all of: {', '.join(self.required_permissions)}"
            else:
                detail = f"Permission denied. Required any of: {', '.join(self.required_permissions)}"
            
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=detail
            )
        
        # Return user_id so it can be used by the route if needed
        return user_id


def require_permission(permission: Permission) -> PermissionChecker:
    """
    Create a dependency that requires a SINGLE permission.
    
    This is the most common use case for permission checking.
    
    Args:
        permission: The Permission enum value required
        
    Returns:
        PermissionChecker instance configured for single permission
        
    Example:
        @router.get(
            "/users",
            dependencies=[Depends(require_permission(Permission.USERS_VIEW))]
        )
        async def list_users():
            ...
    """
    return PermissionChecker(permissions=[permission], require_all=False)


def require_any_permission(*permissions: Permission) -> PermissionChecker:
    """
    Create a dependency that requires ANY ONE of the specified permissions.
    
    Uses OR logic - user needs at least one of the listed permissions.
    Useful for endpoints accessible to multiple roles.
    
    Args:
        *permissions: Variable number of Permission enum values
        
    Returns:
        PermissionChecker instance configured for OR logic
        
    Example:
        @router.get(
            "/dashboard",
            dependencies=[Depends(require_any_permission(
                Permission.ADMIN_ACCESS,
                Permission.REPORTS_VIEW
            ))]
        )
        async def view_dashboard():
            ...
    """
    return PermissionChecker(permissions=list(permissions), require_all=False)


def require_all_permissions(*permissions: Permission) -> PermissionChecker:
    """
    Create a dependency that requires ALL of the specified permissions.
    
    Uses AND logic - user must have every listed permission.
    Useful for highly sensitive operations requiring multiple authorizations.
    
    Args:
        *permissions: Variable number of Permission enum values
        
    Returns:
        PermissionChecker instance configured for AND logic
        
    Example:
        @router.delete(
            "/users/{user_id}",
            dependencies=[Depends(require_all_permissions(
                Permission.USERS_DELETE,
                Permission.ADMIN_ACCESS
            ))]
        )
        async def delete_user(user_id: UUID):
            ...
    """
    return PermissionChecker(permissions=list(permissions), require_all=True)


# =============================================================================
# ALTERNATIVE: Functional Approach (for those who prefer closures)
# =============================================================================

def create_permission_dependency(permission: Permission) -> Callable:
    """
    Alternative functional approach using closures.
    
    This provides the same functionality as PermissionChecker
    but using a closure-based approach instead of a class.
    
    Args:
        permission: The Permission enum value required
        
    Returns:
        Async dependency function
        
    Example:
        @router.get(
            "/users",
            dependencies=[Depends(create_permission_dependency(Permission.USERS_VIEW))]
        )
    """
    @inject
    async def permission_dependency(
        user_id: UUID = Depends(get_current_user),
        permission_service: IPermissionService = Depends(
            Provide[Container.permission_service]
        )
    ) -> UUID:
        has_perm = await permission_service.has_permission(
            user_id, 
            permission.value
        )
        
        if not has_perm:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied. Required: {permission.value}"
            )
        
        return user_id
    
    return permission_dependency


# =============================================================================
# HELPER: Get current user with permissions (for route handlers)
# =============================================================================

class CurrentUserWithPermissions:
    """
    Data class to hold current user info with loaded permissions.
    
    Useful when route handlers need to check permissions dynamically
    or display available actions to the user.
    """
    
    def __init__(self, user_id: UUID, permissions: set[str]):
        self.user_id = user_id
        self.permissions = permissions
    
    def has_permission(self, permission: Permission) -> bool:
        """Check if user has a specific permission."""
        return permission.value in self.permissions
    
    def has_any(self, *permissions: Permission) -> bool:
        """Check if user has any of the specified permissions."""
        perm_values = {p.value for p in permissions}
        return bool(self.permissions & perm_values)


@inject
async def get_current_user_with_permissions(
    user_id: UUID = Depends(get_current_user),
    permission_service: IPermissionService = Depends(
        Provide[Container.permission_service]
    )
) -> CurrentUserWithPermissions:
    """
    Dependency that returns current user with all their permissions loaded.
    
    Use this when you need to check permissions within a route handler
    rather than at the route level.
    
    Example:
        @router.get("/items/{item_id}")
        async def get_item(
            item_id: int,
            current_user: CurrentUserWithPermissions = Depends(
                get_current_user_with_permissions
            )
        ):
            item = await get_item_by_id(item_id)
            
            # Show edit button only if user has permission
            item.can_edit = current_user.has_permission(Permission.ITEMS_UPDATE)
            
            return item
    """
    permissions = await permission_service.get_user_permissions(user_id)
    return CurrentUserWithPermissions(user_id=user_id, permissions=permissions)
