from datetime import datetime, timezone, timedelta
import uuid

from app.core.config import settings
from app.models import role, user_role
from app.repositories.interfaces.user_repository_interface import IUserRepository
from app.schema.response.meta import ResponseMeta
from app.services.interfaces import IAuthService, ITokenService, ICacheService, IEmailService
from app.services.interfaces import IEmailTemplateService
from app.utils.auth_utils import get_password_hash, verify_password
from app.utils.exception_utils import NotFoundException, UnauthorizedException, BadRequestException
from app.schema.response.auth import AuthResponse
from app.schema.response.user import UserResponse, UserRoleResponse, UserRoleResponse


class AuthService(IAuthService):

    def __init__(
        self,
        user_repository: IUserRepository,
        token_service: ITokenService,
        cache_service: ICacheService,
        email_service: IEmailService
        ,
        email_template_service: IEmailTemplateService
    ):
        self.user_repository = user_repository
        self.token_service = token_service
        self.cache_service = cache_service
        self.email_service = email_service
        self.email_template_service = email_template_service

    async def login(self, email: str, password: str) -> AuthResponse:
        # Verify user exists
        user = await self.user_repository.get_by_email_with_roles(email)
        if not user:
            raise NotFoundException(
                key="email",
                message=f"User not found with this email=> {email}",
            )

        # Verify password
        if not verify_password(password, user.password):
            raise UnauthorizedException(
                message="Incorrect username or password!",
            )
        
        # Check if email confirmation is required and user's email is confirmed
        if settings.REQUIRE_EMAIL_CONFIRMED_ACCOUNT and not user.email_confirmed:
            raise UnauthorizedException(
                message="Email not confirmed. Please verify your email address before logging in.",
            )
        
        # Check if user account is active
        if not user.is_active:
            raise UnauthorizedException(
                message="Your account has been deactivated. Please contact support.",
            )

        # Generate tokens
        token_response = self.token_service.create_token_response(user)

        # Update user's refresh token in database
        user.refresh_token = token_response.refresh_token
        user.refresh_token_expiry_time = token_response.refresh_token_expiry_time
        await self.user_repository.update(user)
        
        # await self.cache_service.set(
        #     key=f"user:{user.id}:refresh_token",
        #     value=token_response.refresh_token,
        #     sliding_expiration=None
        # )

        return AuthResponse(
            tokenInfo=token_response,
            userInfo=UserResponse(
                id=user.id,
                email=user.email,
                full_name=user.full_name,
                phone_number=user.phone_number,
                profile_image_url=user.profile_image_url,
                is_active=user.is_active,
                email_confirmed=user.email_confirmed,
                roles=[
                    UserRoleResponse(
                        id=user_role.role.id,
                        name=user_role.role.name,
                        normalized_name=user_role.role.normalized_name
                    )
                    for user_role in (user.roles or [])
                ]
            ),
        )

    async def refresh_token(self, access_token: str, refresh_token: str) -> AuthResponse:
        # Extract user_id from access token
        user_id = self.token_service.get_user_id_from_access_token(access_token)
        if not user_id:
            raise UnauthorizedException(message="Invalid access token!")

        # Fetch user from database
        user = await self.user_repository.get_by_id_with_roles(user_id)
        if not user:
            raise NotFoundException(
                key="user_id",
                message=f"User not found with id: {user_id}"
            )

        # Verify refresh token
        refresh_payload = self.token_service.verify_refresh_token(refresh_token)
        if not refresh_payload:
            raise UnauthorizedException(message="Invalid refresh token!")

        # Verify refresh token matches stored token
        if user.refresh_token != refresh_token:
            raise UnauthorizedException(message="Refresh token does not match!")

        # Check if refresh token is expired
        if user.refresh_token_expiry_time < datetime.now(timezone.utc):
            raise UnauthorizedException(message="Refresh token has expired!")

        # Generate new tokens
        token_response = self.token_service.create_token_response(user)

        # Update user's refresh token in database
        user.refresh_token = token_response.refresh_token
        user.refresh_token_expiry_time = token_response.refresh_token_expiry_time
        await self.user_repository.update(user)

        return AuthResponse(
            tokenInfo=token_response,
            userInfo=UserResponse(
                id=user.id,
                email=user.email,
                full_name=user.full_name,
                phone_number=user.phone_number,
                profile_image_url=user.profile_image_url,
                is_active=user.is_active,
                email_confirmed=user.email_confirmed,
                roles=[
                    UserRoleResponse(
                        id=user_role.role.id,
                        name=user_role.role.name,
                        normalized_name=user_role.role.normalized_name
                    )
                    for user_role in (user.roles or [])
                ]
            ),
        )

    async def forgot_password(self, email: str) -> ResponseMeta:
        """Send password reset verification code to user's email."""
        # Verify user exists
        user = await self.user_repository.get_by_email(email)
        if not user:
            raise NotFoundException(
                key="email",
                message=f"User not found with this email: {email}",
            )
        
        # Check if user account is active
        if not user.is_active:
            raise BadRequestException(
                "account",
                "Your account has been deactivated. Please contact support.",
            )
        
        # Generate verification code (UUID)
        verification_code = uuid.uuid4()
        
        # Set expiry time from settings
        expiry_time = datetime.now(timezone.utc) + timedelta(minutes=settings.FORGOT_PASSWORD_VERIFICATION_CODE_EXPIRE_MINUTES)
        
        # Update user with verification code
        user.forgot_password_verification_code = verification_code
        user.forgot_password_verification_code_expiry_time = expiry_time
        await self.user_repository.update(user)
        
        # Generate password reset link
        reset_link = f"{settings.FRONTEND_URL}/reset-password?code={verification_code}&email={user.email}"

        # Render email template
        body = self.email_template_service.render(
            "reset_password.html",
            {
                "full_name": user.full_name,
                "reset_link": reset_link,
                "expiry_minutes": settings.FORGOT_PASSWORD_VERIFICATION_CODE_EXPIRE_MINUTES,
            },
        )

        # Send email with rendered HTML body
        await self.email_service.send_email_async(
            subject="Password Reset Request",
            body=body,
            receivers={user.email: user.full_name},
        )
        
        return ResponseMeta(message="Password reset verification code sent to your email")

    async def reset_password(self, email: str, verification_code: str, new_password: str) -> ResponseMeta:
        """Reset user password using verification code."""
        # Verify user exists
        user = await self.user_repository.get_by_email(email)
        if not user:
            raise NotFoundException(
                key="email",
                message=f"User not found with this email: {email}",
            )
        
        # Check if verification code exists
        if not user.forgot_password_verification_code:
            raise BadRequestException(
                "verification_code",
                "No password reset request found. Please request a new verification code.",
            )
        
        # Verify the code matches
        if str(user.forgot_password_verification_code) != verification_code:
            raise BadRequestException(
                "verification_code",
                "Invalid verification code!",
            )
        
        # Check if verification code is expired
        if user.forgot_password_verification_code_expiry_time < datetime.now(timezone.utc):
            raise BadRequestException(
                "verification_code",
                "Verification code has expired. Please request a new one.",
            )
        
        # Hash new password
        hashed_password = get_password_hash(new_password)
        
        # Update user password and clear verification code
        user.password = hashed_password
        user.forgot_password_verification_code = None
        user.forgot_password_verification_code_expiry_time = None
        # Invalidate existing refresh token for security
        user.refresh_token = None
        user.refresh_token_expiry_time = None
        await self.user_repository.update(user)
        
        return ResponseMeta(message="Password has been reset successfully. Please login with your new password.")
