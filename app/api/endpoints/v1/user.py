"""  
User Management Endpoints with RBAC Protection

This module provides CRUD operations for user management:
- Search users with pagination
- Create new users
- View user details
- Update existing users
- Delete users
"""

import uuid
from fastapi import APIRouter, Depends, status
from dependency_injector.wiring import inject, Provide
from app.core.rate_limiting import RateLimit

from app.core.container import Container
from app.core.jwt_security import JWTBearer
from app.core.constants.pagination import PAGE, PAGE_SIZE
from app.core.rbac import AppPermissions, require_permission
from app.schema.request.identity.user import UserRequest, UserUpdateRequest
from app.schema.request.identity.profile import ChangeEmailRequest
from app.schema.request.identity.user_status import UserStatusRequest
from app.schema.response.meta import ResponseMeta
from app.schema.response.user import UserResponse, UserSearchResponse, UserRoleResponse
from app.schema.response.pagination import PagedData
from app.services.interfaces.user_service_interface import IUserService


router = APIRouter(
    prefix="/users",
    tags=["Users"],
    dependencies=[Depends(JWTBearer())]  # JWT required for all endpoints
)


# =============================================================================
# SEARCH - Requires USERS_SEARCH permission
# =============================================================================
@router.get(
    "",
    summary="Search users with pagination",
    response_model=PagedData[UserSearchResponse],
    dependencies=[
        Depends(require_permission(AppPermissions.USERS_SEARCH)),
        Depends(RateLimit(requests=60, window=60, key_prefix="users_search")),
    ]
)
@inject
async def search(
    email: str | None = None,
    full_name: str | None = None,
    is_active: bool | None = None,
    page: int = PAGE,
    page_size: int = PAGE_SIZE,
    user_service: IUserService = Depends(Provide[Container.user_service])
):
    """
    Search users with pagination support.
    
    Permission Required:
        - permission.users.search
    """
    return await user_service.search(page, page_size, email, full_name, is_active)


# =============================================================================
# CREATE - Requires USERS_CREATE permission
# =============================================================================
@router.post(
    "",
    summary="Create a new user",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(require_permission(AppPermissions.USERS_CREATE)),
        Depends(RateLimit(requests=10, window=60, key_prefix="users_create")),
    ]
)
@inject
async def create(
    user_request: UserRequest,
    user_service: IUserService = Depends(Provide[Container.user_service])
):
    """
    Create a new user with the provided details.
    
    Permission Required:
        - permission.users.create
    """
    return await user_service.create(user_request)


# =============================================================================
# VIEW - Requires USERS_VIEW permission
# =============================================================================
@router.get(
    "/{id}",
    summary="Get user by Id",
    response_model=UserResponse,
    dependencies=[
        Depends(require_permission(AppPermissions.USERS_VIEW)),
        Depends(RateLimit(requests=120, window=60, key_prefix="users_view")),
    ]
)
@inject
async def get_by_id(
    id: uuid.UUID,
    user_service: IUserService = Depends(Provide[Container.user_service])
):
    """
    Get a specific user by their ID.
    
    Permission Required:
        - permission.users.view
    """
    return await user_service.get_by_id(id)


# =============================================================================
# UPDATE - Requires USERS_UPDATE permission
# =============================================================================
@router.put(
    "/{id}",
    summary="Update user",
    response_model=UserResponse,
    dependencies=[
        Depends(require_permission(AppPermissions.USERS_UPDATE)),
        Depends(RateLimit(requests=20, window=60, key_prefix="users_update")),
    ]
)
@inject
async def update(
    id: uuid.UUID,
    user_request: UserUpdateRequest,
    user_service: IUserService = Depends(Provide[Container.user_service])
):
    """
    Update an existing user.
    
    Permission Required:
        - permission.users.update
    """
    return await user_service.update(id, user_request)


@router.patch(
    "/{id}/email",
    summary="Change user email",
    response_model=ResponseMeta,
    dependencies=[
        Depends(require_permission(AppPermissions.USERS_UPDATE)),
        Depends(RateLimit(requests=5, window=60, key_prefix="users_change_email")),
    ]
)
@inject
async def change_user_email(
    id: uuid.UUID,
    request: ChangeEmailRequest,
    user_service: IUserService = Depends(Provide[Container.user_service])
):
    """Change another user's email (requires `permission.users.update`)."""
    return await user_service.change_email(id, request.email)

# =============================================================================
# GET ROLES - Requires USERS_VIEW permission
# =============================================================================
@router.get(
    "/{id}/roles",
    summary="Get user roles",
    response_model=list[UserRoleResponse],
    dependencies=[
        Depends(require_permission(AppPermissions.USERS_VIEW)),
        Depends(RateLimit(requests=120, window=60, key_prefix="users_roles")),
    ]
)
@inject
async def get_user_roles(
    id: uuid.UUID,
    user_service: IUserService = Depends(Provide[Container.user_service])
):
    """
    Get all roles assigned to a specific user.
    
    Permission Required:
        - permission.users.view
    """
    return await user_service.get_user_roles(id)


# =============================================================================
# UPDATE STATUS - Requires USERS_UPDATE permission
# =============================================================================
@router.patch(
    "/{id}/status",
    summary="Update user status",
    response_model=UserResponse,
    dependencies=[
        Depends(require_permission(AppPermissions.USERS_UPDATE)),
        Depends(RateLimit(requests=20, window=60, key_prefix="users_update_status")),
    ]
)
@inject
async def update_status(
    id: uuid.UUID,
    status_request: UserStatusRequest,
    user_service: IUserService = Depends(Provide[Container.user_service])
):
    """
    Update user's active status.
    
    Permission Required:
        - permission.users.update
    """
    return await user_service.update_status(id, status_request.is_active)



# =============================================================================
# DELETE - Requires USERS_DELETE permission
# =============================================================================
@router.delete(
    "/{id}",
    summary="Delete user",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[
        Depends(require_permission(AppPermissions.USERS_DELETE)),
        Depends(RateLimit(requests=5, window=60, key_prefix="users_delete")),
    ]
)
@inject
async def delete(
    id: uuid.UUID,
    user_service: IUserService = Depends(Provide[Container.user_service])
):
    """
    Delete a user by ID.
    
    Permission Required:
        - permission.users.delete
    """
    await user_service.delete(id)