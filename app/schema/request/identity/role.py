
import re
from typing import Annotated

from pydantic import BaseModel, Field, field_validator
from pydantic_core import PydanticCustomError


class RoleRequest(BaseModel):
    name: Annotated[str, Field(min_length=1, description="Role name (alphanumeric only)")]
    description: str | None = None

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v or not v.strip():
            raise PydanticCustomError(
                'name_required',
                'Name is required'
            )
        if not re.match(r'^[a-zA-Z0-9]+$', v.strip()):
            raise PydanticCustomError(
                'name_alphanumeric',
                'Name must contain only alphanumeric characters'
            )
        return v.strip()
