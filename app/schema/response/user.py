from pydantic import BaseModel
import uuid

class UserBaseResponse(BaseModel):
    """Base user response with common fields."""
    id: uuid.UUID
    email: str
    full_name: str
    phone_number: str | None
    profile_image_url: str | None
    is_active: bool
    email_confirmed: bool

class UserRoleResponse(BaseModel):
    """User role response with role details."""
    name: str
    normalized_name: str

class UserResponse(UserBaseResponse):
    """Full user response with all details."""
    roles: list[UserRoleResponse] = []

class UserSearchResponse(UserBaseResponse):
    """Response for user search/list - without sensitive details."""
    pass