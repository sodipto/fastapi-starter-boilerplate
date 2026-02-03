import uuid
from sqlalchemy import select, func, or_

from app.core.constants.pagination import calculate_skip
from app.models.user import User
from app.models.user_role import UserRole
from app.repositories.interfaces.user_repository_interface import IUserRepository
from app.repositories.interfaces.role_repository_interface import IRoleRepository
from app.schema.request.identity.user import UserRequest, UserUpdateRequest
from app.schema.response.user import UserResponse, UserRoleResponse, UserSearchResponse
from app.schema.response.pagination import PagedData, create_paged_response
from app.services.interfaces import IUserService
from app.utils.exception_utils import NotFoundException, ConflictException
from app.utils.auth_utils import get_password_hash


class UserService(IUserService):
    def __init__(self, user_repository: IUserRepository, role_repository: IRoleRepository):
        self.user_repository = user_repository
        self.role_repository = role_repository

    def _to_response(self, user: User) -> UserResponse:
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
            filters.append(User.email.ilike(f"%{email}%"))
        if full_name:
            filters.append(User.full_name.ilike(f"%{full_name}%"))
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

        # Validate role IDs if provided
        if user_request.role_ids:
            for role_id in user_request.role_ids:
                role = await self.role_repository.get_by_id(role_id)
                if not role:
                    raise NotFoundException(
                        "role_id",
                        f"Role with id {role_id} not found"
                    )
                
        # Create user
        user = User(
            email=user_request.email,
            normalized_email=user_request.email.upper(),
            full_name=user_request.full_name,
            phone_number=user_request.phone_number,
            password_hash=get_password_hash(user_request.password),
            is_active=user_request.is_active,
            email_confirmed=False
        )

        created_user = await self.user_repository.create(user)

        # Assign roles if provided
        if user_request.role_ids:
            await self.user_repository.assign_roles(created_user.id, user_request.role_ids)

        # Reload user with roles
        created_user = await self.user_repository.get_by_id_with_roles(created_user.id)
        
        return self._to_response(created_user)

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
            for role_id in user_request.role_ids:
                role = await self.role_repository.get_by_id(role_id)
                if not role:
                    raise NotFoundException(
                        "role_id",
                        f"Role with id {role_id} not found"
                    )

        updated_user = await self.user_repository.update(user)

        # Update roles if provided
        if user_request.role_ids is not None:
            await self.user_repository.assign_roles(user_id, user_request.role_ids)

        # Reload user with updated roles
        updated_user = await self.user_repository.get_by_id_with_roles(user_id)
        
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
