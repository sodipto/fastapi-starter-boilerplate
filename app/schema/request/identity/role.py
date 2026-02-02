
import re
from typing import Annotated

from pydantic import BaseModel, Field, field_validator, model_validator
from pydantic_core import PydanticCustomError

from app.core.rbac import AppPermissions


class RoleRequest(BaseModel):
    name: Annotated[str, Field(min_length=1, description="Role name (alphanumeric only)")]
    description: str | None = None
    claims: list[str] = Field(..., min_length=1, description="List of permission claim names (at least one required)")

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

    @field_validator('claims')
    @classmethod
    def validate_claims(cls, v: list[str]) -> list[str]:
        if not v:
            return v
        
        # Get all valid permission names (lowercase for comparison)
        valid_permissions = {perm.name.lower(): perm.name for perm in AppPermissions.all()}
        
        # Normalize and validate claims
        normalized_claims = []
        invalid_claims = []
        
        for claim in v:
            claim_lower = claim.lower()
            if claim_lower in valid_permissions:
                # Use the canonical lowercase format
                normalized_claims.append(valid_permissions[claim_lower])
            else:
                invalid_claims.append(claim)
        
        if invalid_claims:
            raise PydanticCustomError(
                'invalid_claims',
                f"Invalid permission claims: {', '.join(invalid_claims)}"
            )
        
        # Remove duplicates while preserving order
        return list(dict.fromkeys(normalized_claims))
