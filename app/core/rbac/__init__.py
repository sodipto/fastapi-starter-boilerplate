"""
RBAC (Role-Based Access Control) Module

This module provides a complete permission-based authorization system
for FastAPI applications.

Components:
    - AppAction: Enum of all available actions (View, Search, Create, etc.)
    - AppResource: Enum of all available resources (Users, Roles, etc.)
    - AppClaim: Claim type constants
    - PermissionDefinition: Permission record combining action + resource with metadata
    - AppPermissions: Central registry of all permissions
    - PermissionClaimType: Enum for claim type values
    - PermissionGroups: Predefined permission groups
    - require_permission: Dependency for single permission check
    - require_any_permission: Dependency for OR logic permission check
    - require_all_permissions: Dependency for AND logic permission check
    - get_current_user_with_permissions: Get user with loaded permissions

Usage:
    from app.core.rbac import AppPermissions, require_permission
    
    @router.get("/users", dependencies=[Depends(require_permission(AppPermissions.USERS_VIEW))])
    async def list_users():
        ...
"""

from app.core.rbac.actions import AppAction
from app.core.rbac.resources import AppResource
from app.core.rbac.claims import AppClaim, PermissionClaimType
from app.core.rbac.permission_definition import PermissionDefinition
from app.core.rbac.app_permissions import AppPermissions
from app.core.rbac.app_roles import AppRoles, ApplicationSystemRole
from app.core.rbac.groups import PermissionGroups
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
    # Permission classes
    "AppAction",
    "AppResource",
    "AppClaim",
    "PermissionDefinition",
    "AppPermissions",
    "PermissionClaimType",
    "PermissionGroups",
    # Role classes
    "AppRoles",
    "ApplicationSystemRole",
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
