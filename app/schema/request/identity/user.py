import re
import uuid
from typing import Annotated

from pydantic import BaseModel, EmailStr, Field, field_validator
from pydantic_core import PydanticCustomError


class UserRequest(BaseModel):
    """Request schema for creating/updating users."""
    
    email: Annotated[EmailStr, Field(description="User email address")]
    full_name: Annotated[str, Field(min_length=1, max_length=100, description="Full name of the user")]
    phone_number: str | None = Field(None, description="Phone number (optional)")
    password: Annotated[str, Field(min_length=8, description="User password (min 8 characters)")] | None = None
    is_active: bool = Field(True, description="Whether the user account is active")
    role_ids: list[uuid.UUID] = Field(default_factory=list, description="List of role IDs to assign to the user")

    @field_validator('full_name')
    @classmethod
    def validate_full_name(cls, v: str) -> str:
        if not v or not v.strip():
            raise PydanticCustomError(
                'full_name_required',
                'Full name is required'
            )
        return v.strip()

    @field_validator('phone_number')
    @classmethod
    def validate_phone_number(cls, v: str | None) -> str | None:
        if v is None or not v.strip():
            return None
        # Basic phone number validation (can be customized)
        cleaned = re.sub(r'[^\d+\-() ]', '', v.strip())
        if len(cleaned) < 10:
            raise PydanticCustomError(
                'phone_number_invalid',
                'Phone number must be at least 10 digits'
            )
        return cleaned

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str | None) -> str | None:
        if v is None:
            return None
        if len(v) < 8:
            raise PydanticCustomError(
                'password_too_short',
                'Password must be at least 8 characters long'
            )
        return v


class UserUpdateRequest(BaseModel):
    """Request schema for updating users (password optional)."""
    
    full_name: Annotated[str, Field(min_length=1, max_length=100, description="Full name of the user")] | None = None
    phone_number: str | None = None
    is_active: bool | None = None
    role_ids: list[uuid.UUID] | None = None

    @field_validator('full_name')
    @classmethod
    def validate_full_name(cls, v: str | None) -> str | None:
        if v is None:
            return None
        if not v.strip():
            raise PydanticCustomError(
                'full_name_required',
                'Full name cannot be empty'
            )
        return v.strip()

    @field_validator('phone_number')
    @classmethod
    def validate_phone_number(cls, v: str | None) -> str | None:
        if v is None or not v.strip():
            return None
        cleaned = re.sub(r'[^\d+\-() ]', '', v.strip())
        if len(cleaned) < 10:
            raise PydanticCustomError(
                'phone_number_invalid',
                'Phone number must be at least 10 digits'
            )
        return cleaned
