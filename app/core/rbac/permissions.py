"""
Permission Enums for Role-Based Access Control (RBAC)

This module defines all available permissions in the application using Enum classes.
Using Enums instead of raw strings provides:
- Type safety and IDE auto-completion
- Centralized permission management
- Easy refactoring and maintenance
- Compile-time error detection for typos

Permission Naming Convention:
    {RESOURCE}_{ACTION}
    
Examples:
    - USERS_VIEW: Permission to view users
    - USERS_CREATE: Permission to create users
    - ROLES_DELETE: Permission to delete roles
"""

from enum import Enum


class Permission(str, Enum):
    """
    Application-wide permission definitions.
    
    Inherits from str to allow direct string comparison and serialization.
    Each permission follows the pattern: RESOURCE_ACTION
    
    Usage:
        @router.get("/users", dependencies=[Depends(require_permission(Permission.USERS_VIEW))])
        async def get_users():
            ...
    """
    
    # =============================================================================
    # USER MANAGEMENT PERMISSIONS
    # =============================================================================
    USERS_SEARCH = "users.search"       # Search/list users
    USERS_VIEW = "users.view"           # View single user details
    USERS_CREATE = "users.create"       # Create new users
    USERS_UPDATE = "users.update"       # Update existing users
    USERS_DELETE = "users.delete"       # Delete users
    
    # =============================================================================
    # ROLE MANAGEMENT PERMISSIONS
    # =============================================================================
    ROLES_SEARCH = "roles.search"       # Search/list roles
    ROLES_VIEW = "roles.view"           # View single role details
    ROLES_CREATE = "roles.create"       # Create new roles
    ROLES_UPDATE = "roles.update"       # Update role details and permissions
    ROLES_DELETE = "roles.delete"       # Delete roles
    
    # =============================================================================
    # DOCUMENT PERMISSIONS
    # =============================================================================
    DOCUMENTS_SEARCH = "documents.search"   # Search/list documents
    DOCUMENTS_VIEW = "documents.view"       # View single document
    DOCUMENTS_UPLOAD = "documents.upload"   # Upload documents
    DOCUMENTS_DELETE = "documents.delete"   # Delete documents
    DOCUMENTS_UPDATE = "documents.update"   # Update document metadata
    
    # =============================================================================
    # SYSTEM/ADMIN PERMISSIONS
    # =============================================================================
    ADMIN_ACCESS = "admin.access"       # Access admin panel
    SYSTEM_SETTINGS = "system.settings" # Manage system settings
    AUDIT_VIEW = "audit.view"           # View audit logs
    

class PermissionClaimType(str, Enum):
    """
    Claim types used in RoleClaim tables.
    
    This defines the 'claim_type' field value for permission claims.
    """
    PERMISSION = "permission"           # Standard permission claim
    ROLE = "role"                       # Role membership claim
    SCOPE = "scope"                     # OAuth scope claim


class PermissionGroups:
    """
    Predefined permission groups for common use cases.
    
    Usage:
        dependencies=[Depends(require_any_permission(*PermissionGroups.USER_MANAGEMENT))]
    """
    
    # All user-related permissions
    USER_MANAGEMENT = [
        Permission.USERS_SEARCH,
        Permission.USERS_VIEW,
        Permission.USERS_CREATE,
        Permission.USERS_UPDATE,
        Permission.USERS_DELETE,
    ]
    
    # All role-related permissions
    ROLE_MANAGEMENT = [
        Permission.ROLES_SEARCH,
        Permission.ROLES_VIEW,
        Permission.ROLES_CREATE,
        Permission.ROLES_UPDATE,
        Permission.ROLES_DELETE,
    ]
    
    # Admin permissions
    ADMIN = [
        Permission.ADMIN_ACCESS,
        Permission.SYSTEM_SETTINGS,
    ]
