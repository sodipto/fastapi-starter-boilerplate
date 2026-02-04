"""
Application Roles Registry

Defines system roles and their configurations.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class ApplicationSystemRole:
    """System role definition."""
    name: str
    normalized_name: str
    description: str
    is_editable: bool = False


class AppRoles:
    """
    Central registry of system roles in the application.
    
    Usage:
        # Get all system roles
        roles = AppRoles.all()
        
        # Check role constants
        if role.normalized_name == AppRoles.SUPER_ADMIN:
            ...
    """
    
    # Role name constants
    SUPER_ADMIN = "SUPER_ADMIN"
    ADMIN = "ADMIN"
    CUSTOMER = "CUSTOMER"
    
    # System role definitions
    _system_roles: list[ApplicationSystemRole] = [
        ApplicationSystemRole(
            name="Super Admin",
            normalized_name=SUPER_ADMIN,
            description="Role with all permissions",
            is_editable=False
        ),
        ApplicationSystemRole(
            name="Admin",
            normalized_name=ADMIN,
            description="Administrator role with management permissions",
            is_editable=False
        ),
        ApplicationSystemRole(
            name="Customer",
            normalized_name=CUSTOMER,
            description="Customer role with limited permissions",
            is_editable=False
        ),
    ]
    
    @classmethod
    def all(cls) -> list[ApplicationSystemRole]:
        """Get all system roles."""
        return cls._system_roles
