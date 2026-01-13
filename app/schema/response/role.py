from pydantic import BaseModel
import uuid

class RoleResponse(BaseModel):
    id: uuid.UUID
    name: str
    normalized_name: str
    description: str | None = None
    is_system: bool