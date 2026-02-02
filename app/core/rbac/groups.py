"""
Permission Groups for RBAC

Predefined permission groups for common use cases.
"""

from app.core.rbac.app_permissions import AppPermissions


class PermissionGroups:
    """
    Predefined permission groups for common use cases.
    
    Usage:
        dependencies=[Depends(require_any_permission(*PermissionGroups.USER_MANAGEMENT))]
    """
    
    # All user-related permissions
    USER_MANAGEMENT = [
        AppPermissions.USERS_SEARCH,
        AppPermissions.USERS_VIEW,
        AppPermissions.USERS_CREATE,
        AppPermissions.USERS_UPDATE,
        AppPermissions.USERS_DELETE,
    ]
    
    # All role-related permissions
    ROLE_MANAGEMENT = [
        AppPermissions.ROLES_SEARCH,
        AppPermissions.ROLES_VIEW,
        AppPermissions.ROLES_CREATE,
        AppPermissions.ROLES_UPDATE,
        AppPermissions.ROLES_DELETE,
    ]
