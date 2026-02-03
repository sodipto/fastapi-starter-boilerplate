from abc import ABC, abstractmethod
import uuid

from app.schema.request.identity.user import UserRequest, UserUpdateRequest
from app.schema.response.user import UserResponse, UserSearchResponse
from app.schema.response.pagination import PagedData


class IUserService(ABC):
    """Interface for user service operations."""

    @abstractmethod
    async def get_by_id(self, user_id: uuid.UUID) -> UserResponse:
        """Get user by ID."""
        pass

    @abstractmethod
    async def search(
        self,
        page: int,
        page_size: int,
        email: str | None = None,
        full_name: str | None = None,
        is_active: bool | None = None
    ) -> PagedData[UserSearchResponse]:
        """Search users with pagination."""
        pass

    @abstractmethod
    async def create(self, user_request: UserRequest) -> UserResponse:
        """Create a new user."""
        pass

    @abstractmethod
    async def update(self, user_id: uuid.UUID, user_request: UserUpdateRequest) -> UserResponse:
        """Update an existing user."""
        pass

    @abstractmethod
    async def delete(self, user_id: uuid.UUID) -> None:
        """Delete a user."""
        pass
