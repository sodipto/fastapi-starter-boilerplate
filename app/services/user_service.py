import uuid
from sqlalchemy import select, func, or_

from app.core.constants.pagination import calculate_skip
from app.models.user import User
from app.models.user_role import UserRole
from app.repositories.interfaces.user_repository_interface import IUserRepository
from app.repositories.interfaces.role_repository_interface import IRoleRepository
from app.services.interfaces import IEmailService, IEmailTemplateService
from app.schema.response.meta import ResponseMeta
from app.core.config import settings
from datetime import datetime, timezone, timedelta
import uuid
from app.schema.request.identity.user import UserRequest, UserUpdateRequest
from app.schema.request.auth.signup import SignupRequest
from app.core.rbac import AppRoles
from app.schema.response.user import UserResponse, UserRoleResponse, UserSearchResponse
from app.schema.response.pagination import PagedData, create_paged_response
from app.services.interfaces import IUserService
from app.utils.exception_utils import NotFoundException, ConflictException, BadRequestException
from app.utils.auth_utils import get_password_hash
from app.services.interfaces.permission_service_interface import IPermissionService


class UserService(IUserService):
    def __init__(
        self,
        user_repository: IUserRepository,
        role_repository: IRoleRepository,
        email_service: IEmailService,
        email_template_service: IEmailTemplateService,
        permission_service: IPermissionService
    ):
        self.user_repository = user_repository
        self.role_repository = role_repository
        self.email_service = email_service
        self.email_template_service = email_template_service
        self.permission_service = permission_service

    def _to_response(self, user: User) -> UserResponse:
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

    async def get_by_id(self, user_id: uuid.UUID) -> UserResponse:
        """Get user by ID."""
        user = await self.user_repository.get_by_id_with_roles(user_id)

        if not user:
            raise NotFoundException(
                "user_id",
                f"User with id {user_id} not found"
            )

        return self._to_response(user)

    async def search(
        self,
        page: int,
        page_size: int,
        email: str | None = None,
        full_name: str | None = None,
        is_active: bool | None = None
    ) -> PagedData[UserSearchResponse]:
        """Search users with pagination."""
        skip = calculate_skip(page, page_size)
        
        # Build query filters
        filters = []
        if email:
            filters.append(func.lower(User.email) == email.lower())
        if full_name:
            filters.append(User.full_name.ilike(f"{full_name}%"))
        if is_active is not None:
            filters.append(User.is_active == is_active)
        
        # Execute query with pagination
        users, total = await self.user_repository.get_all_paginated(
            skip=skip,
            limit=page_size,
            filters=filters
        )

        user_responses = [
            UserSearchResponse(
                id=user.id,
                email=user.email,
                full_name=user.full_name,
                phone_number=user.phone_number,
                profile_image_url=user.profile_image_url,
                is_active=user.is_active,
                email_confirmed=user.email_confirmed
            )
            for user in users
        ]

        return create_paged_response(user_responses, total, page, page_size)

    async def create(self, user_request: UserRequest) -> UserResponse:
        """Create a new user."""
        # Check if email already exists
        existing_user = await self.user_repository.get_by_email(user_request.email)
        if existing_user:
            raise ConflictException(
                "email",
                f"User with email '{user_request.email}' already exists"
            )

        # Validate role ids if provided
        if user_request.role_ids:
            existing_roles = await self.role_repository.get_by_ids(user_request.role_ids)
            existing_role_ids = {role.id for role in existing_roles}
            
            # Find missing role IDs
            missing_role_ids = [role_id for role_id in user_request.role_ids if role_id not in existing_role_ids]
            if missing_role_ids:
                raise NotFoundException(
                    "role_id",
                    f"Roles with ids {missing_role_ids} not found"
                )
                
        # Create user and assign roles within one session to ensure FK consistency
        user = User(
            email=user_request.email.lower(),
            full_name=user_request.full_name,
            phone_number=user_request.phone_number,
            password=get_password_hash(user_request.password),
            is_active=user_request.is_active,
            email_confirmed=False
        )

        async with self.user_repository.db_factory() as session:
            session.add(user)
            await session.flush()

            if user_request.role_ids:
                await self.user_repository.assign_roles_in_session(session, user.id, user_request.role_ids)

            await session.commit()

            created_user = user

        # Reload user with roles
        created_user = await self.user_repository.get_by_id_with_roles(created_user.id)
        return self._to_response(created_user)

    async def signup(self, signup_request: SignupRequest) -> ResponseMeta:
        """Create user, assign CUSTOMER role and send email confirmation."""
        # Check if email already exists
        existing_user = await self.user_repository.get_by_email(signup_request.email)
        if existing_user:
            raise ConflictException(
                "email",
                f"User with email '{signup_request.email.lower()}' already exists"
            )
        
        role = await self.role_repository.get_by_normalized_name(AppRoles.CUSTOMER)
        if not role:
            raise NotFoundException(
                "role",
                f"System role '{AppRoles.CUSTOMER}' not found. Please seed system roles."
            )

        # Create user and assign CUSTOMER role within same session to avoid FK issues
        user = User(
            email=signup_request.email.lower(),
            full_name=signup_request.full_name,
            phone_number=signup_request.phone_number,
            password=get_password_hash(signup_request.password),
            is_active=not settings.REQUIRE_EMAIL_CONFIRMED_ACCOUNT,
            email_confirmed=False,
        )

        async with self.user_repository.db_factory() as session:
            session.add(user)
            await session.flush()

            await self.user_repository.assign_roles_in_session(session, user.id, [role.id])

            # If email confirmation is required, set verification fields now so they persist in same transaction
            if settings.REQUIRE_EMAIL_CONFIRMED_ACCOUNT:
                verification_code = uuid.uuid4()
                expiry_time = datetime.now(timezone.utc) + timedelta(minutes=settings.EMAIL_VERIFICATION_CODE_EXPIRE_MINUTES)
                user.email_verification_code = verification_code
                user.email_verification_code_expiry_time = expiry_time

            await session.commit()

            created_user = user

        # If email confirmation required, send email after commit
        if settings.REQUIRE_EMAIL_CONFIRMED_ACCOUNT:
            confirm_link = f"{settings.FRONTEND_URL}/confirm-email?code={created_user.email_verification_code}&email={created_user.email}"
            body = self.email_template_service.render(
                "confirm_email.html",
                {"full_name": created_user.full_name, "confirm_link": confirm_link, "expiry_minutes": settings.EMAIL_VERIFICATION_CODE_EXPIRE_MINUTES},
            )
            await self.email_service.send_email_async(
                subject="Confirm your email",
                body=body,
                receivers={created_user.email: created_user.full_name},
            )
            return ResponseMeta(message="Signup successful. Confirmation email sent.")

        return ResponseMeta(message="Signup successful.")

    async def confirm_email(self, email: str, verification_code: str) -> ResponseMeta:
        user = await self.user_repository.get_by_email(email)
        if not user:
            raise NotFoundException("email", f"User not found with this email: {email}")

        if not user.email_verification_code:
            raise BadRequestException(
                "verification_code",
                "No confirmation request found. Please request a new confirmation email."
            )

        if str(user.email_verification_code) != verification_code:
            raise BadRequestException(
                "verification_code",
                "Invalid verification code!"
            )

        if user.email_verification_code_expiry_time < datetime.now(timezone.utc):
            raise BadRequestException(
                "verification_code",
                "Verification code has expired. Please request a new one."
            )

        user.is_active = True
        user.email_confirmed = True
        user.email_verification_code = None
        user.email_verification_code_expiry_time = None
        # Single update, safe to auto-commit
        await self.user_repository.update(user)

        return ResponseMeta(message="Email confirmed successfully.")

    async def resend_confirmation(self, email: str) -> ResponseMeta:
        user = await self.user_repository.get_by_email(email)
        if not user:
            raise NotFoundException("email", f"User not found with this email: {email}")

        if user.email_confirmed:
            return ResponseMeta(message="Email already confirmed.")
        await self._generate_verification_and_send_email(user)
        await self.user_repository.commit()
        return ResponseMeta(message="Confirmation email resent.")

    async def _generate_verification_and_send_email(self, user: User) -> None:
        """Generate verification code, persist it, and send confirmation email."""
        verification_code = uuid.uuid4()
        expiry_time = datetime.now(timezone.utc) + timedelta(minutes=settings.EMAIL_VERIFICATION_CODE_EXPIRE_MINUTES)
        user.email_verification_code = verification_code
        user.email_verification_code_expiry_time = expiry_time
        await self.user_repository.update(user, auto_commit=False) # We will handle commit in caller

        confirm_link = f"{settings.FRONTEND_URL}/confirm-email?code={verification_code}&email={user.email}"
        body = self.email_template_service.render(
            "confirm_email.html",
            {"full_name": user.full_name, "confirm_link": confirm_link, "expiry_minutes": settings.EMAIL_VERIFICATION_CODE_EXPIRE_MINUTES},
        )
        await self.email_service.send_email_async(
            subject="Confirm your email",
            body=body,
            receivers={user.email: user.full_name},
        )

    async def update(self, user_id: uuid.UUID, user_request: UserUpdateRequest) -> UserResponse:
        """Update an existing user."""
        user = await self.user_repository.get_by_id_with_roles(user_id)

        if not user:
            raise NotFoundException(
                "user_id",
                f"User with id {user_id} not found"
            )

        # Update fields if provided
        user.full_name = user_request.full_name
        user.is_active = user_request.is_active
        if user_request.phone_number is not None:
            user.phone_number = user_request.phone_number
        

        # Validate role IDs if provided
        if user_request.role_ids is not None:
            existing_roles = await self.role_repository.get_by_ids(user_request.role_ids)
            existing_role_ids = {role.id for role in existing_roles}
            
            # Find missing role IDs
            missing_role_ids = [role_id for role_id in user_request.role_ids if role_id not in existing_role_ids]
            if missing_role_ids:
                raise NotFoundException(
                    "role_id",
                    f"Roles with ids {missing_role_ids} not found"
                )

        # Update user fields
        updated_user = await self.user_repository.update(user, auto_commit=False)

        # Update roles within same session for atomicity
        async with self.user_repository.db_factory() as session:
            session.add(updated_user)
            await session.flush()
            if user_request.role_ids is not None:
                await self.user_repository.assign_roles_in_session(session, user_id, user_request.role_ids)
            await session.commit()

        # Reload user with updated roles
        updated_user = await self.user_repository.get_by_id_with_roles(user_id)

        # Invalidate permission cache for this user so permission checks reflect updates
        try:
            await self.permission_service.invalidate_user_permissions_cache(user_id)
        except Exception:
            # Don't fail the update if cache invalidation fails; log elsewhere if needed
            pass

        return self._to_response(updated_user)

    async def delete(self, user_id: uuid.UUID) -> None:
        """Delete a user."""
        user = await self.user_repository.get_by_id(user_id)

        if not user:
            raise NotFoundException(
                "user_id",
                f"User with id {user_id} not found"
            )

        await self.user_repository.delete(user_id)

    async def get_user_roles(self, user_id: uuid.UUID) -> list[UserRoleResponse]:
        """Get all roles assigned to a user."""
        user = await self.user_repository.get_by_id_with_roles(user_id)

        if not user:
            raise NotFoundException(
                "user_id",
                f"User with id {user_id} not found"
            )

        return [
            UserRoleResponse(
                name=user_role.role.name,
                normalized_name=user_role.role.normalized_name
            )
            for user_role in (user.roles or [])
        ]

    async def update_status(self, user_id: uuid.UUID, is_active: bool) -> UserResponse:
        """Update user's active status."""
        user = await self.user_repository.get_by_id_with_roles(user_id)

        if not user:
            raise NotFoundException(
                "user_id",
                f"User with id {user_id} not found"
            )

        user.is_active = is_active
        await self.user_repository.update(user)

        return self._to_response(user)
