from pydantic import BaseModel
import uuid


class RoleBaseResponse(BaseModel):
    """Base role response with common fields."""
    id: uuid.UUID
    name: str
    normalized_name: str
    description: str | None = None
    is_system: bool


class RoleSearchResponse(RoleBaseResponse):
    """Response for role search/list - without claims for performance."""
    pass


class RoleResponse(RoleBaseResponse):
    """Full role response with claims - for get by id, create, update."""
    claims: list[str] = []