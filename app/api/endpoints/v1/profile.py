from uuid import UUID
from fastapi import APIRouter
from fastapi.params import Depends
from dependency_injector.wiring import inject, Provide
from app.core.rate_limiting import RateLimit

from app.core.container import Container
from app.core.identity import get_current_user_id
from app.core.jwt_security import JWTBearer
from app.schema.response.meta import ResponseMeta
from app.schema.response.user import UserResponse
from app.schema.request.identity.profile import UpdateProfileRequest, ChangePasswordRequest
from app.services.interfaces.profile_service_interface import IProfileService
from app.utils.exception_utils import BadRequestException


router = APIRouter(
    prefix="/profile",
    tags=["Profile"],
    dependencies=[Depends(JWTBearer())]
)


@router.get(
    "",
    summary="Get current user profile",
    response_model=UserResponse,
    dependencies=[Depends(RateLimit(requests=120, window=60, key_prefix="profile_get"))]
)
@inject
async def get_profile(
    user_id: UUID = Depends(get_current_user_id),
    profile_service: IProfileService = Depends(Provide[Container.profile_service])
):
    """
    Get the profile of the currently logged-in user.
    
    """
    return await profile_service.get_profile(user_id)


@router.put(
    "",
    summary="Update current user profile",
    response_model=UserResponse,
    dependencies=[Depends(RateLimit(requests=30, window=60, key_prefix="profile_update"))]
)
@inject
async def update_profile(
    request: UpdateProfileRequest,
    user_id: UUID = Depends(get_current_user_id),
    profile_service: IProfileService = Depends(Provide[Container.profile_service])
):
    """
    Update the profile of the currently logged-in user.
    
    Args:
        request: UpdateProfileRequest containing full_name and phone_number
        
    Returns:
        UserResponse: Updated user profile information
    """
    return await profile_service.update_profile(user_id=user_id, request=request)


@router.put(
    "/password",
    summary="Change current user password",
    response_model=ResponseMeta,
    dependencies=[Depends(RateLimit(requests=3, window=60, key_prefix="profile_change_password"))]
)
@inject
async def change_password(
    request: ChangePasswordRequest,
    user_id: UUID = Depends(get_current_user_id),
    profile_service: IProfileService = Depends(Provide[Container.profile_service])
):
    """
    Change the password of the currently logged-in user.
    
    Requires:
        - Current password for verification
        - New password matching confirmation
        
    Args:
        request: ChangePasswordRequest with current_password and new_password
        
    Returns:
        ResponseMeta: Success message
        
    Raises:
        UnauthorizedException: If current password is incorrect
        BadRequestException: If new password doesn't match confirmation
    """
    if request.new_password != request.confirm_password:
        raise BadRequestException(
            key="password",
            message="New password and confirmation do not match"
        )
    
    return await profile_service.change_password(
        user_id=user_id,
        current_password=request.current_password,
        new_password=request.new_password
    )
