import uuid
from collections import defaultdict

from app.core.constants.pagination import calculate_skip
from app.core.rbac import AppPermissions, PermissionClaimType
from app.models.role import Role
from app.models.role_claim import RoleClaim
from app.repositories.interfaces.role_repository_interface import IRoleRepository
from app.schema.request.identity.role import RoleRequest
from app.schema.response.role import RoleResponse, RoleSearchResponse
from app.schema.response.permission import PermissionResponse, PermissionClaimResponse
from app.schema.response.pagination import PagedData, create_paged_response
from app.services.interfaces.role_service_interface import IRoleService
from app.utils.exception_utils import NotFoundException, ForbiddenException, ConflictException


class RoleService(IRoleService):
    def __init__(self, role_repository: IRoleRepository):
        self.role_repository = role_repository

    def _extract_permission_claims(self, role: Role) -> list[str]:
        """Extract permission claim names from role."""
        if not role.role_claims:
            return []
        return [
            claim.claim_name 
            for claim in role.role_claims 
            if claim.claim_type == PermissionClaimType.PERMISSION.value
        ]

    def _to_response(self, role: Role) -> RoleResponse:
        """Convert Role model to RoleResponse."""
        return RoleResponse(
            id=role.id,
            name=role.name,
            normalized_name=role.normalized_name,
            description=role.description,
            is_system=role.is_system,
            claims=self._extract_permission_claims(role)
        )

    def get_all_permissions(self) -> list[PermissionResponse]:
        """Get all available permissions in the system, grouped by resource."""
        permissions = AppPermissions.visible()
        
        # Group permissions by display_name (resource)
        grouped: dict[str, list[PermissionClaimResponse]] = defaultdict(list)
        
        for perm in permissions:
            claim = PermissionClaimResponse(
                action=perm.action.value,
                description=perm.description,
                permission=perm.name  # Use canonical lowercase format: permission.users.search
            )
            grouped[perm.display_name].append(claim)
        
        # Convert to list of PermissionResponse
        return [
            PermissionResponse(name=name, claims=claims)
            for name, claims in grouped.items()
        ]

    async def create(self, role_request: RoleRequest) -> RoleResponse:
        """Create a new role with optional claims."""
        # Check if role name already exists
        if await self.role_repository.name_exists(role_request.name):
            raise ConflictException(
                "role_name",
                f"Role with name '{role_request.name}' already exists"
            )

        trimmed_name = role_request.name.strip()
        normalized = trimmed_name.upper().replace(" ", "_")

        # Create new role
        role = Role(
            name=trimmed_name,
            normalized_name=normalized,
            description=role_request.description.strip() if role_request.description is not None else None,
            is_system=False,
        )

        # Ensure checks use trimmed name
        
        # Create role and sync claims in a single session/transaction for atomicity
        async with self.role_repository.db_factory() as session:
            session.add(role)
            await session.flush()
            if role_request.claims:
                await self.role_repository.sync_role_claims_in_session(
                    session, role.id, role_request.claims
                )
            await session.commit()
            created_role = role

        # Reload role to get claims
        created_role = await self.role_repository.get_by_id(created_role.id)

        return self._to_response(created_role)

    async def get_by_id(self, role_id: uuid.UUID) -> RoleResponse:
        """Get role by id."""
        role = await self.role_repository.get_by_id(role_id)

        if not role:
            raise NotFoundException(
                "role_id",
                f"Role with id {role_id} not found"
            )

        return self._to_response(role)

    async def search(self, page: int, page_size: int, name: str | None = None, is_system: bool | None = None) -> PagedData[RoleSearchResponse]:
        """Search roles with pagination."""
        skip = calculate_skip(page, page_size)
        roles, total = await self.role_repository.get_all_paginated(skip, page_size, name, is_system)

        role_responses = [
            RoleSearchResponse(
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
        """Update an existing role with claims sync."""
        role = await self.role_repository.get_by_id(role_id)

        if not role:
            raise NotFoundException(
                "role_id",
                f"Role with id {role_id} not found"
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

        # Trim incoming name and update normalized_name (spaces -> underscores)
        trimmed_name = role_request.name.strip()
        role.name = trimmed_name
        role.normalized_name = trimmed_name.upper().replace(" ", "_")
        role.description = role_request.description.strip() if role_request.description is not None else None

        # Update role and sync claims in a single session/transaction for atomicity
        async with self.role_repository.db_factory() as session:
            session.add(role)
            await session.flush()
            if role_request.claims:
                await self.role_repository.sync_role_claims_in_session(
                    session, role_id, role_request.claims
                )
            await session.commit()
            updated_role = role

        # Reload role to get updated claims
        updated_role = await self.role_repository.get_by_id(role_id)

        return self._to_response(updated_role)

    async def delete(self, role_id: uuid.UUID) -> bool:
        """Delete a role by id."""
        role = await self.role_repository.get_by_id(role_id)

        if not role:
            raise NotFoundException(
                "role_id",
                f"Role with id {role_id} not found"
            )

        # Check if it's a system role
        if role.is_system:
            raise ForbiddenException(
                "system_role",
                "System roles cannot be deleted"
            )

        # Check if role is assigned to any users
        has_users, user_count = await self.role_repository.has_users(role_id)
        if has_users:
            raise ConflictException(
                "role_in_use",
                f"Cannot delete role '{role.name}' because it is assigned to {user_count} user(s). Please remove the role from all users before deleting."
            )

        result = await self.role_repository.delete(role_id)
        return result
