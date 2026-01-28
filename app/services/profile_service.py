from app.repositories.interfaces.profile_repository_interface import IProfileRepository
from app.schema.response.user import UserResponse
from app.services.interfaces.profile_service_interface import IProfileService
from app.utils.auth_utils import verify_password, get_password_hash
from app.utils.exception_utils import NotFoundException, UnauthorizedException, BadRequestException


class ProfileService(IProfileService):
    """Service for user profile operations."""
    
    def __init__(self, profile_repository: IProfileRepository):
        self.profile_repository = profile_repository

    async def get_profile(self, user_id: int) -> UserResponse:
        """Get current user's profile."""
        user = await self.profile_repository.get_user_by_id(user_id)
        if not user:
            raise NotFoundException(
                key="user_id",
                message=f"User not found with id: {user_id}"
            )
        return UserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name
        )

    async def update_profile(self, user_id: int, full_name: str, email: str) -> UserResponse:
        """Update user's profile information."""
        user = await self.profile_repository.get_user_by_id(user_id)
        if not user:
            raise NotFoundException(
                key="user_id",
                message=f"User not found with id: {user_id}"
            )
        
        # Check if email is already taken by another user
        existing_user = await self.profile_repository.get_user_by_email(email)
        if existing_user and existing_user.id != user.id:
            raise BadRequestException(
                key="email",
                message=f"Email {email} is already in use"
            )
        
        user.full_name = full_name
        user.email = email.lower()
        
        updated_user = await self.profile_repository.update_user(user)
        return UserResponse(
            id=updated_user.id,
            email=updated_user.email,
            full_name=updated_user.full_name
        )

    async def change_password(self, user_id: int, current_password: str, new_password: str) -> dict:
        """Change user's password."""
        user = await self.profile_repository.get_user_by_id(user_id)
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
        await self.profile_repository.update_user(user)
        
        return {"message": "Password changed successfully"}
