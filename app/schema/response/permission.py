from pydantic import BaseModel


class PermissionClaimResponse(BaseModel):
    """Response model for a permission claim within a resource group."""
    
    action: str
    """The action (e.g., 'Search', 'View', 'Create')"""
    
    description: str
    """Brief description of what the permission allows"""
    
    permission: str
    """The full permission string (e.g., 'Permission.Roles.Search')"""


class PermissionResponse(BaseModel):
    """Response model for a permission group by resource."""
    
    name: str
    """The resource/group name (e.g., 'Roles', 'Users')"""
    
    claims: list[PermissionClaimResponse]
    """List of permission claims for this resource"""
