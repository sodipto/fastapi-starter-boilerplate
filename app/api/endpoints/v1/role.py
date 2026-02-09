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
from app.core.rate_limiting import RateLimit

from app.core.container import Container
from app.core.jwt_security import JWTBearer
from app.core.constants.pagination import PAGE, PAGE_SIZE
from app.core.rbac import AppPermissions, require_permission
from app.schema.request.identity.role import RoleRequest
from app.schema.response.role import RoleResponse, RoleSearchResponse
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
    dependencies=[
        Depends(require_permission(AppPermissions.ROLES_CREATE)),
        Depends(RateLimit(requests=10, window=60, key_prefix="roles_create")),
    ]
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
    response_model=PagedData[RoleSearchResponse],
    dependencies=[
        Depends(require_permission(AppPermissions.ROLES_SEARCH)),
        Depends(RateLimit(requests=60, window=60, key_prefix="roles_search")),
    ]
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
    "/{id}",
    summary="Get role by id",
    response_model=RoleResponse,
    dependencies=[
        Depends(require_permission(AppPermissions.ROLES_VIEW)),
        Depends(RateLimit(requests=120, window=60, key_prefix="roles_view")),
    ]
)
@inject
async def get(
    id: uuid.UUID,
    role_service: IRoleService = Depends(Provide[Container.role_service])
):
    """
    Get a specific role by its id.
    
    Permission Required:
        - permission.roles.view
    """
    return await role_service.get_by_id(id)


# =============================================================================
# UPDATE - Requires ROLES_UPDATE permission
# =============================================================================
@router.put(
    "/{id}",
    summary="Update role",
    response_model=RoleResponse,
    dependencies=[
        Depends(require_permission(AppPermissions.ROLES_UPDATE)),
        Depends(RateLimit(requests=20, window=60, key_prefix="roles_update")),
    ]
)
@inject
async def update(
    id: uuid.UUID,
    role_request: RoleRequest,
    role_service: IRoleService = Depends(Provide[Container.role_service])
):
    """
    Update an existing role. System roles cannot be updated.
    
    Permission Required:
        - permission.roles.update
    """
    return await role_service.update(id, role_request)


# =============================================================================
# DELETE - Requires ROLES_DELETE permission
# =============================================================================
@router.delete(
    "/{id}",
    summary="Delete role",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[
        Depends(require_permission(AppPermissions.ROLES_DELETE)),
        Depends(RateLimit(requests=5, window=60, key_prefix="roles_delete")),
    ]
)
@inject
async def delete(
    id: uuid.UUID,
    role_service: IRoleService = Depends(Provide[Container.role_service])
):
    """
    Delete a role by id. System roles cannot be deleted.
    
    Permission Required:
        - permission.roles.delete
    """
    await role_service.delete(id)
