import uuid
from fastapi import APIRouter, Depends, status
from dependency_injector.wiring import inject, Provide

from app.core.container import Container
from app.core.jwt_security import JWTBearer
from app.schema.request.identity.role import RoleRequest
from app.schema.response.role import RoleResponse
from app.services.interfaces.role_service_interface import IRoleService


router = APIRouter(
    prefix="/roles",
    tags=["Roles"],
    dependencies=[Depends(JWTBearer())]
)


@router.post(
    "/",
    summary="Create a new role",
    response_model=RoleResponse,
    status_code=status.HTTP_201_CREATED
)
@inject
async def create(
    role_request: RoleRequest,
    role_service: IRoleService = Depends(Provide[Container.role_service])
):
    """Create a new role with the provided details."""
    return await role_service.create(role_request)


@router.get(
    "/search",
    summary="Search roles with pagination",
    response_model=dict
)
@inject
async def search(
    skip: int = 0,
    limit: int = 20,
    role_service: IRoleService = Depends(Provide[Container.role_service])
):
    """Search all roles with pagination support."""
    return await role_service.search(skip, limit)


@router.get(
    "/{role_id}",
    summary="Get role by ID",
    response_model=RoleResponse
)
@inject
async def get(
    role_id: uuid.UUID,
    role_service: IRoleService = Depends(Provide[Container.role_service])
):
    """Get a specific role by its ID."""
    return await role_service.get_by_id(role_id)


@router.put(
    "/{role_id}",
    summary="Update role",
    response_model=RoleResponse
)
@inject
async def update(
    role_id: uuid.UUID,
    role_request: RoleRequest,
    role_service: IRoleService = Depends(Provide[Container.role_service])
):
    """Update an existing role. System roles cannot be updated."""
    return await role_service.update(role_id, role_request)


@router.delete(
    "/{role_id}",
    summary="Delete role",
    status_code=status.HTTP_204_NO_CONTENT
)
@inject
async def delete(
    role_id: uuid.UUID,
    role_service: IRoleService = Depends(Provide[Container.role_service])
):
    """Delete a role by ID. System roles cannot be deleted."""
    await role_service.delete(role_id)
