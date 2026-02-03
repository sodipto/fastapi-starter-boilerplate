import uuid

from app.repositories.interfaces.user_repository_interface import IUserRepository
from app.schema.response.user import UserResponse, UserRoleResponse
from app.services.interfaces.profile_service_interface import IProfileService
from app.utils.auth_utils import verify_password, get_password_hash
from app.utils.exception_utils import NotFoundException, UnauthorizedException, BadRequestException


class ProfileService(IProfileService):
    """Service for user profile operations."""
    
    def __init__(self, user_repository: IUserRepository):
        self.user_repository = user_repository

    async def get_profile(self, user_id: uuid.UUID) -> UserResponse:
        """Get current user's profile."""
        user = await self.user_repository.get_by_id_with_roles(user_id)
        if not user:
            raise NotFoundException(
                key="user_id",
                message=f"User not found with id: {user_id}"
            )
        
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

    async def update_profile(self, user_id: uuid.UUID, full_name: str, email: str) -> UserResponse:
        """Update user's profile information."""
        user = await self.user_repository.get_by_id_with_roles(user_id)
        if not user:
            raise NotFoundException(
                key="user_id",
                message=f"User not found with id: {user_id}"
            )
        
        # Check if email is already taken by another user
        existing_user = await self.user_repository.get_by_email(email)
        if existing_user and existing_user.id != user.id:
            raise BadRequestException(
                key="email",
                message=f"Email {email} is already in use"
            )
        
        user.full_name = full_name
        user.email = email.lower()
        
        updated_user = await self.user_repository.update(user)
        
        roles = [
            UserRoleResponse(
                name=user_role.role.name,
                normalized_name=user_role.role.normalized_name
            )
            for user_role in (updated_user.roles or [])
        ]
        
        return UserResponse(
            id=updated_user.id,
            email=updated_user.email,
            full_name=updated_user.full_name,
            phone_number=updated_user.phone_number,
            profile_image_url=updated_user.profile_image_url,
            is_active=updated_user.is_active,
            email_confirmed=updated_user.email_confirmed,
            roles=roles
        )

    async def change_password(self, user_id: uuid.UUID, current_password: str, new_password: str) -> dict:
        """Change user's password."""
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise NotFoundException(
                key="user_id",
                message=f"User not found with id: {user_id}"
            )
        
        # Verify current password
        if not verify_password(current_password, user.password):
            raise UnauthorizedException(
                message="Current password is incorrect"
            )
        
        # Update password
        user.password = get_password_hash(new_password)
        await self.user_repository.update(user)
        
        return {"message": "Password changed successfully"}
