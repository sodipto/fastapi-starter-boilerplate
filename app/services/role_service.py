import uuid

from app.core.constants.pagination import calculate_skip
from app.models.role import Role
from app.repositories.interfaces.role_repository_interface import IRoleRepository
from app.schema.request.identity.role import RoleRequest
from app.schema.response.role import RoleResponse
from app.schema.response.pagination import PagedData, create_paged_response
from app.services.interfaces.role_service_interface import IRoleService
from app.utils.exception_utils import NotFoundException, ForbiddenException, ConflictException


class RoleService(IRoleService):
    def __init__(self, role_repository: IRoleRepository):
        self.role_repository = role_repository

    async def create(self, role_request: RoleRequest) -> RoleResponse:
        """Create a new role."""
        # Check if role name already exists
        if await self.role_repository.name_exists(role_request.name):
            raise ConflictException(
                "role_name",
                f"Role with name '{role_request.name}' already exists"
            )

        # Create new role
        role = Role(
            name=role_request.name,
            normalized_name=role_request.name.upper(),
            description=role_request.description,
            is_system=False
        )

        created_role = await self.role_repository.create(role)

        return RoleResponse(
            id=created_role.id,
            name=created_role.name,
            normalized_name=created_role.normalized_name,
            description=created_role.description,
            is_system=created_role.is_system
        )

    async def get_by_id(self, role_id: uuid.UUID) -> RoleResponse:
        """Get role by ID."""
        role = await self.role_repository.get_by_id(role_id)

        if not role:
            raise NotFoundException(
                "role_id",
                f"Role with ID {role_id} not found"
            )

        return RoleResponse(
            id=role.id,
            name=role.name,
            normalized_name=role.normalized_name,
            description=role.description,
            is_system=role.is_system
        )

    async def search(self, page: int, page_size: int, is_system: bool | None = None) -> PagedData[RoleResponse]:
        """Search roles with pagination."""
        skip = calculate_skip(page, page_size)
        roles, total = await self.role_repository.get_all_paginated(skip, page_size, is_system)

        role_responses = [
            RoleResponse(
                id=role.id,
                name=role.name,
                normalized_name=role.normalized_name,
                description=role.description,
                is_system=role.is_system
            )
            for role in roles
        ]

        return create_paged_response(role_responses, total, page, page_size)

    async def update(self, role_id: uuid.UUID, role_request: RoleRequest) -> RoleResponse:
        """Update an existing role."""
        role = await self.role_repository.get_by_id(role_id)

        if not role:
            raise NotFoundException(
                "role_id",
                f"Role with ID {role_id} not found"
            )

        # Check if it's a system role
        if role.is_system:
            raise ForbiddenException(
                "system_role",
                "System roles cannot be updated"
            )

        # Check if new name already exists (excluding current role)
        if await self.role_repository.name_exists(role_request.name, exclude_id=role_id):
            raise ConflictException(
                "role_name",
                f"Role with name '{role_request.name}' already exists"
            )

        # Update role
        role.name = role_request.name
        role.normalized_name = role_request.name.upper()
        role.description = role_request.description

        updated_role = await self.role_repository.update(role)

        return RoleResponse(
            id=updated_role.id,
            name=updated_role.name,
            normalized_name=updated_role.normalized_name,
            description=updated_role.description,
            is_system=updated_role.is_system
        )

    async def delete(self, role_id: uuid.UUID) -> bool:
        """Delete a role by ID."""
        role = await self.role_repository.get_by_id(role_id)

        if not role:
            raise NotFoundException(
                "role_id",
                f"Role with ID {role_id} not found"
            )

        # Check if it's a system role
        if role.is_system:
            raise ForbiddenException(
                "system_role",
                "System roles cannot be deleted"
            )

        return await self.role_repository.delete(role_id)
