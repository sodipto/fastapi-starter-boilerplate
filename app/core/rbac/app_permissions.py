"""
Application Permissions Registry

Central registry of all permissions in the application.
"""

from app.core.rbac.actions import AppAction
from app.core.rbac.resources import AppResource
from app.core.rbac.api_permission import APIPermission


class AppPermissions:
    """
    Central registry of all permissions in the application.
    
    Usage:
        # Get all permissions
        all_perms = AppPermissions.all()
        
        # Get visible permissions only
        visible = AppPermissions.visible()
        
        # Get a specific permission name
        perm_name = AppPermissions.USERS_VIEW.name
    """
    
    # =========================================================================
    # USER MANAGEMENT PERMISSIONS
    # =========================================================================
    USERS_SEARCH = APIPermission(
        description="Search users",
        display_name="Users",
        action=AppAction.SEARCH,
        resource=AppResource.USERS,
    )
    USERS_VIEW = APIPermission(
        description="View user details",
        display_name="Users",
        action=AppAction.VIEW,
        resource=AppResource.USERS,
    )
    USERS_CREATE = APIPermission(
        description="Create new users",
        display_name="Users",
        action=AppAction.CREATE,
        resource=AppResource.USERS,
    )
    USERS_UPDATE = APIPermission(
        description="Update existing users",
        display_name="Users",
        action=AppAction.UPDATE,
        resource=AppResource.USERS,
    )
    USERS_DELETE = APIPermission(
        description="Delete users",
        display_name="Users",
        action=AppAction.DELETE,
        resource=AppResource.USERS,
    )
    
    # =========================================================================
    # ROLE MANAGEMENT PERMISSIONS
    # =========================================================================
    ROLES_SEARCH = APIPermission(
        description="Search roles",
        display_name="Roles",
        action=AppAction.SEARCH,
        resource=AppResource.ROLES
    )
    ROLES_VIEW = APIPermission(
        description="View role details",
        display_name="Roles",
        action=AppAction.VIEW,
        resource=AppResource.ROLES
    )
    ROLES_CREATE = APIPermission(
        description="Create new roles",
        display_name="Roles",
        action=AppAction.CREATE,
        resource=AppResource.ROLES
    )
    ROLES_UPDATE = APIPermission(
        description="Update roles and permissions",
        display_name="Roles",
        action=AppAction.UPDATE,
        resource=AppResource.ROLES
    )
    ROLES_DELETE = APIPermission(
        description="Delete roles",
        display_name="Roles",
        action=AppAction.DELETE,
        resource=AppResource.ROLES
    )

    # =========================================================================
    # DOCUMENT PERMISSIONS
    # =========================================================================
    DOCUMENTS_VIEW = APIPermission(
        description="View documents",
        display_name="Documents",
        action=AppAction.VIEW,
        resource=AppResource.DOCUMENTS
    )
    DOCUMENTS_UPLOAD = APIPermission(
        description="Upload documents",
        display_name="Documents",
        action=AppAction.UPLOAD,
        resource=AppResource.DOCUMENTS
    )
    DOCUMENTS_UPDATE = APIPermission(
        description="Update document metadata",
        display_name="Documents",
        action=AppAction.UPDATE,
        resource=AppResource.DOCUMENTS
    )
    DOCUMENTS_DELETE = APIPermission(
        description="Delete documents",
        display_name="Documents",
        action=AppAction.DELETE,
        resource=AppResource.DOCUMENTS
    )
    
    # =========================================================================
    # PERMISSION REGISTRY
    # =========================================================================
    _all_permissions: list[APIPermission] = None
    
    @classmethod
    def all(cls) -> list[APIPermission]:
        """Get all permissions in the application."""
        if cls._all_permissions is None:
            cls._all_permissions = [
                # Users
                cls.USERS_SEARCH,
                cls.USERS_VIEW,
                cls.USERS_CREATE,
                cls.USERS_UPDATE,
                cls.USERS_DELETE,
                # Roles
                cls.ROLES_SEARCH,
                cls.ROLES_VIEW,
                cls.ROLES_CREATE,
                cls.ROLES_UPDATE,
                cls.ROLES_DELETE,
                # Documents
                cls.DOCUMENTS_VIEW,
                cls.DOCUMENTS_UPLOAD,
                cls.DOCUMENTS_UPDATE,
                cls.DOCUMENTS_DELETE,
            ]
        return cls._all_permissions
    
    @classmethod
    def visible(cls) -> list[APIPermission]:
        """Get only visible permissions (is_show=True)."""
        return [p for p in cls.all() if p.is_show]
    
    @classmethod
    def by_resource(cls, resource: AppResource) -> list[APIPermission]:
        """Get all permissions for a specific resource."""
        return [p for p in cls.all() if p.resource == resource]

    # =========================================================================
    # ROLE-BASED PERMISSION SETS
    # =========================================================================
    @classmethod
    def super_admin(cls) -> list[APIPermission]:
        """Get all permissions for Super Admin role."""
        return cls.all()
    
    @classmethod
    def basic_user(cls) -> list[APIPermission]:
        """Get basic permissions for regular users."""
        return [
            cls.USERS_VIEW,
            cls.DOCUMENTS_VIEW,
        ]
