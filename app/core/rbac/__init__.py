"""
RBAC (Role-Based Access Control) Module

This module provides a complete permission-based authorization system
for FastAPI applications.

Components:
    - Permission: Enum class defining all available permissions
    - PermissionClaimType: Enum for claim type values
    - PermissionGroups: Predefined permission groups
    - require_permission: Dependency for single permission check
    - require_any_permission: Dependency for OR logic permission check
    - require_all_permissions: Dependency for AND logic permission check
    - get_current_user_with_permissions: Get user with loaded permissions

Usage:
    from app.core.rbac import Permission, require_permission
    
    @router.get("/users", dependencies=[Depends(require_permission(Permission.USERS_VIEW))])
    async def list_users():
        ...
"""

from app.core.rbac.permissions import Permission, PermissionClaimType, PermissionGroups
from app.core.rbac.dependencies import (
    PermissionChecker,
    require_permission,
    require_any_permission,
    require_all_permissions,
    create_permission_dependency,
    CurrentUserWithPermissions,
    get_current_user_with_permissions,
)

__all__ = [
    # Permission enums and groups
    "Permission",
    "PermissionClaimType",
    "PermissionGroups",
    # Dependencies
    "PermissionChecker",
    "require_permission",
    "require_any_permission",
    "require_all_permissions",
    "create_permission_dependency",
    # Helpers
    "CurrentUserWithPermissions",
    "get_current_user_with_permissions",
]
