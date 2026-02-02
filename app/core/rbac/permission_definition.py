"""
Permission Definition

Defines the PermissionDefinition dataclass that combines action and resource with metadata.
"""

from dataclasses import dataclass

from app.core.rbac.actions import AppAction
from app.core.rbac.resources import AppResource
from app.core.rbac.claims import AppClaim


@dataclass(frozen=True)
class PermissionDefinition:
    """
    A permission record combining action and resource with metadata.
    
    Attributes:
        description: Brief description of what the permission allows
        display_name: Human-readable name for UI display
        action: The action (from AppAction)
        resource: The resource (from AppResource)
        is_show: Whether to show in UI (default True)
    """
    description: str
    display_name: str
    action: AppAction
    resource: AppResource
    is_show: bool = True
    
    @property
    def name(self) -> str:
        """Generate permission name: permission.{resource}.{action}"""
        return self.name_for(self.action, self.resource)
    
    @staticmethod
    def name_for(action: AppAction, resource: AppResource) -> str:
        """Generate permission name from action and resource."""
        return f"{AppClaim.PERMISSION}.{resource.value}.{action.value}"
