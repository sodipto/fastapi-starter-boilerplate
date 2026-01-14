from abc import ABC, abstractmethod
import uuid

from app.schema.request.identity.role import RoleRequest
from app.schema.response.role import RoleResponse
from app.schema.response.pagination import PagedData


class IRoleService(ABC):
    """Interface for role service operations."""

    @abstractmethod
    async def create(self, role_request: RoleRequest) -> RoleResponse:
        """Create a new role."""
        pass

    @abstractmethod
    async def get_by_id(self, role_id: uuid.UUID) -> RoleResponse:
        """Get role by ID."""
        pass

    @abstractmethod
    async def search(self, page: int, page_size: int, name: str | None = None, is_system: bool | None = None) -> PagedData[RoleResponse]:
        """Search roles with pagination."""
        pass

    @abstractmethod
    async def update(self, role_id: uuid.UUID, role_request: RoleRequest) -> RoleResponse:
        """Update an existing role."""
        pass

    @abstractmethod
    async def delete(self, role_id: uuid.UUID) -> bool:
        """Delete a role by ID."""
        pass
