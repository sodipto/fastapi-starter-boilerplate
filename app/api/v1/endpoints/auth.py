import re
from typing import Annotated
import uuid
from fastapi import APIRouter, Depends
from dependency_injector.wiring import inject, Provide
from pydantic import BaseModel,EmailStr, Field, field_validator
from pydantic_core import PydanticCustomError

from app.core.container import Container
from app.services.auth_service import AuthService
from app.utils.auth_utils import create_access_token

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

EMAIL_REGEX = re.compile(
    r"\A(?:[a-zA-Z0-9!#$%&'*+/=?^_`{|}~-]+"
    r"(?:\.[a-zA-Z0-9!#$%&'*+/=?^_`{|}~-]+)*@"
    r"(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]*[a-zA-Z0-9])?\.)+"
    r"[a-zA-Z0-9](?:[a-zA-Z0-9-]*[a-zA-Z0-9])?)\Z"
)
class LoginRequest(BaseModel):
    email: str
    password: Annotated[str, Field(description="Password must be between 6 and 8 characters")]

    @field_validator("email")
    def check_email_format(cls, value):
        if not EMAIL_REGEX.match(value):
            raise PydanticCustomError(
                "invalid_email_format",
                "Email must be a valid email address!"
            )
        return value
    
    @field_validator("password")
    def check_password(cls, v: str) -> str:
        if not (6 <= len(v) <= 8):
            raise PydanticCustomError(
                "password_length",
                "Password must be between 6 and 8 characters!"
            )
        return v

@router.post("/login")
@inject
async def login(
    payload: LoginRequest,
    auth_service: AuthService = Depends(Provide[Container.auth_service])
):
    user = await auth_service.authenticate_user(payload.email, payload.password)
    
    access_token = create_access_token(
        data={
            "id": str(user.Id),
            "username": user.FullName,
            "email": user.Email,
            "code": str(uuid.uuid4()),
        }
    )

    return {
        "token_type": "bearer",
        "access_token": access_token,
        "user": {
            "id": str(user.Id),
            "username": user.FullName,
            "email": user.Email,
        },
    }