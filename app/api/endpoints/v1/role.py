"""  
Role Management Endpoints with RBAC Protection

This module demonstrates production-ready permission-based authorization:
- Single permission protection
- Multiple permissions with OR logic  
- Multiple permissions with AND logic
"""

import uuid
from fastapi import APIRouter, Depends, status
from dependency_injector.wiring import inject, Provide

from app.core.container import Container
from app.core.jwt_security import JWTBearer
from app.core.constants.pagination import PAGE, PAGE_SIZE
from app.core.rbac import AppPermissions, require_permission
from app.schema.request.identity.role import RoleRequest
from app.schema.response.role import RoleResponse
from app.schema.response.permission import PermissionResponse
from app.schema.response.pagination import PagedData
from app.services.interfaces.role_service_interface import IRoleService


router = APIRouter(
    prefix="/roles",
    tags=["Roles"],
    dependencies=[Depends(JWTBearer())]  # JWT required for all endpoints
)


# =============================================================================
# PERMISSIONS - Get all available permissions (for role assignment UI)
# =============================================================================
@router.get(
    "/permissions",
    summary="Get all available permissions",
    response_model=list[PermissionResponse]
)
@inject
async def get_all_permissions(
    role_service: IRoleService = Depends(Provide[Container.role_service])
):
    """
    Get all available permissions in the system.
    
    Args:
        visible_only: If True, return only permissions with is_show=True (default).
                     If False, return all permissions including hidden ones.
    
    Returns a list of all permissions with their metadata.
    Useful for building role permission assignment UI.
    
    No specific permission required - any authenticated user can view.
    """
    return role_service.get_all_permissions()


# =============================================================================
# CREATE - Requires ROLES_CREATE permission
# =============================================================================
@router.post(
    "/",
    summary="Create a new role",
    response_model=RoleResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission(AppPermissions.ROLES_CREATE))]
)
@inject
async def create(
    role_request: RoleRequest,
    role_service: IRoleService = Depends(Provide[Container.role_service])
):
    """
    Create a new role with the provided details.
    
    Permission Required:
        - permission.roles.create
    """
    return await role_service.create(role_request)


# =============================================================================
# SEARCH - Requires ROLES_SEARCH permission
# =============================================================================
@router.get(
    "/search",
    summary="Search roles with pagination",
    response_model=PagedData[RoleResponse],
    dependencies=[Depends(require_permission(AppPermissions.ROLES_SEARCH))]
)
@inject
async def search(
    name: str | None = None,
    page: int = PAGE,
    page_size: int = PAGE_SIZE,
    is_system: bool | None = None,
    role_service: IRoleService = Depends(Provide[Container.role_service])
):
    """
    Search roles with pagination support.
    
    Permission Required:
        - permission.roles.search
    """
    return await role_service.search(page, page_size, name, is_system)


# =============================================================================
# VIEW - Requires ROLES_VIEW permission
# =============================================================================
@router.get(
    "/{role_id}",
    summary="Get role by id",
    response_model=RoleResponse,
    dependencies=[Depends(require_permission(AppPermissions.ROLES_VIEW))]
)
@inject
async def get(
    role_id: uuid.UUID,
    role_service: IRoleService = Depends(Provide[Container.role_service])
):
    """
    Get a specific role by its id.
    
    Permission Required:
        - permission.roles.view
    """
    return await role_service.get_by_id(role_id)


# =============================================================================
# UPDATE - Requires ROLES_UPDATE permission
# =============================================================================
@router.put(
    "/{role_id}",
    summary="Update role",
    response_model=RoleResponse,
    dependencies=[Depends(require_permission(AppPermissions.ROLES_UPDATE))]
)
@inject
async def update(
    role_id: uuid.UUID,
    role_request: RoleRequest,
    role_service: IRoleService = Depends(Provide[Container.role_service])
):
    """
    Update an existing role. System roles cannot be updated.
    
    Permission Required:
        - permission.roles.update
    """
    return await role_service.update(role_id, role_request)


# =============================================================================
# DELETE - Requires ROLES_DELETE permission
# =============================================================================
@router.delete(
    "/{role_id}",
    summary="Delete role",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission(AppPermissions.ROLES_DELETE))]
)
@inject
async def delete(
    role_id: uuid.UUID,
    role_service: IRoleService = Depends(Provide[Container.role_service])
):
    """
    Delete a role by id. System roles cannot be deleted.
    
    Permission Required:
        - permission.roles.delete
    """
    await role_service.delete(role_id)
