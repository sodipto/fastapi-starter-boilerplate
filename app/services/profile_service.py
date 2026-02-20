import uuid
from datetime import datetime, timezone, timedelta

from app.repositories.interfaces.user_repository_interface import IUserRepository
from app.schema.request.identity.profile import UpdateProfileRequest
from app.schema.response.meta import ResponseMeta
from app.schema.response.user import UserResponse, UserRoleResponse
from app.services.interfaces.profile_service_interface import IProfileService
from app.services.interfaces import IEmailService, IEmailTemplateService
from app.utils.auth_utils import verify_password, get_password_hash
from app.utils.exception_utils import NotFoundException, UnauthorizedException, BadRequestException, ConflictException
from app.core.config import settings


class ProfileService(IProfileService):
    """Service for user profile operations."""
    
    def __init__(
        self,
        user_repository: IUserRepository,
        email_service: IEmailService,
        email_template_service: IEmailTemplateService,
    ):
        self.user_repository = user_repository
        self.email_service = email_service
        self.email_template_service = email_template_service

    def _to_response(self, user) -> UserResponse:
        """Convert User model to UserResponse."""
        roles = [
            UserRoleResponse(
                id=user_role.role.id,
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

    async def _generate_verification_and_send_email(self, user, email: str) -> None:
        """Generate verification code, persist it in a single DB session, and send confirmation email."""
        verification_code = uuid.uuid4()
        expiry_time = datetime.now(timezone.utc) + timedelta(minutes=settings.EMAIL_VERIFICATION_CODE_EXPIRE_MINUTES)

        # Perform DB update inside a single session so flush/commit persist changes
        async with self.user_repository.db_factory() as session:
            user.email = email.lower()
            user.is_active = not settings.REQUIRE_EMAIL_CONFIRMED_ACCOUNT
            user.email_confirmed = False
            user.email_verification_code = verification_code
            user.email_verification_code_expiry_time = expiry_time

            session.add(user)
            await session.flush()

            confirm_link = f"{settings.FRONTEND_URL}/confirm-email?code={verification_code}&email={email}"
            body = self.email_template_service.render(
                "confirm_email.html",
                {"full_name": user.full_name, "confirm_link": confirm_link, "expiry_minutes": settings.EMAIL_VERIFICATION_CODE_EXPIRE_MINUTES},
            )
            # Send email while transaction is still open; if sending fails, transaction will rollback
            await self.email_service.send_email_async(
                subject="Confirm your email",
                body=body,
                receivers={email: user.full_name},
            )

            await session.commit()

    async def change_email(self, user_id: uuid.UUID, email: str) -> ResponseMeta:
        """Change user's email and send verification if required."""
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise NotFoundException(
                key="user_id",
                message=f"User not found with id: {user_id}"
            )

        # if trying to set same email, no-op
        if user.email.lower() == email.lower():
            raise BadRequestException(key="email", message="New email is the same as current email")

        # Check email uniqueness
        existing = await self.user_repository.get_by_email(email)
        if existing:
            raise ConflictException(key="email", message=f"User with email '{email}' already exists")

        # If email confirmation is required, generate verification and send email
        if settings.REQUIRE_EMAIL_CONFIRMED_ACCOUNT:
            await self._generate_verification_and_send_email(user, email)
            return ResponseMeta(message="Email change requested. Confirmation email sent.")

        # If confirmation not required, directly update email and mark confirmed
        user.email = email.lower()
        user.email_confirmed = True
        await self.user_repository.update(user)

        return ResponseMeta(message="Email updated successfully.")
