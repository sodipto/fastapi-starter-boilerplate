import uuid

from app.repositories.interfaces.user_repository_interface import IUserRepository
from app.schema.request.identity.profile import UpdateProfileRequest
from app.schema.response.meta import ResponseMeta
from app.schema.response.user import UserResponse, UserRoleResponse
from app.services.interfaces.profile_service_interface import IProfileService
from app.utils.auth_utils import verify_password, get_password_hash
from app.utils.exception_utils import NotFoundException, UnauthorizedException, BadRequestException


class ProfileService(IProfileService):
    """Service for user profile operations."""
    
    def __init__(self, user_repository: IUserRepository):
        self.user_repository = user_repository

    def _to_response(self, user) -> UserResponse:
        """Convert User model to UserResponse."""
        roles = [
            UserRoleResponse(
                name=user_role.role.name,
                normalized_name=user_role.role.normalized_name
            )
            for user_role in (user.roles or [])
        ]
        
        return UserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            phone_number=user.phone_number,
            profile_image_url=user.profile_image_url,
            is_active=user.is_active,
            email_confirmed=user.email_confirmed,
            roles=roles
        )

    async def get_profile(self, user_id: uuid.UUID) -> UserResponse:
        """Get current user's profile."""
        user = await self.user_repository.get_by_id_with_roles(user_id)
        if not user:
            raise NotFoundException(
                key="user_id",
                message=f"User not found with id: {user_id}"
            )
        
        return self._to_response(user)

    async def update_profile(self, user_id: uuid.UUID, request: UpdateProfileRequest) -> UserResponse:
        """Update user's profile information."""
        user = await self.user_repository.get_by_id_with_roles(user_id)
        if not user:
            raise NotFoundException(
                key="user_id",
                message=f"User not found with id: {user_id}"
            )
        
        user.full_name = request.full_name
        if request.phone_number is not None:
            user.phone_number = request.phone_number
        
        updated_user = await self.user_repository.update(user)
        
        return self._to_response(updated_user)

    async def change_password(self, user_id: uuid.UUID, current_password: str, new_password: str) -> ResponseMeta:
        """Change user's password."""
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise NotFoundException(
                key="user_id",
                message=f"User not found with id: {user_id}"
            )
        
        # Verify current password
        if not verify_password(current_password, user.password):
            raise BadRequestException(
                key="current_password",
                message="Current password is incorrect"
            )
        
        # Update password
        user.password = get_password_hash(new_password)
        await self.user_repository.update(user)
        
        return ResponseMeta(message="Password changed successfully")
