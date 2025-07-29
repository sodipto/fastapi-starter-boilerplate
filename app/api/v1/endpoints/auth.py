import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from dependency_injector.wiring import inject, Provide
from pydantic import BaseModel,EmailStr, Field

from app.core.container import Container
from app.services.auth_service import AuthService
from app.utils.auth_utils import create_access_token

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=8)

@router.post("/login")
@inject
async def login(
    payload: LoginRequest,
    auth_service: AuthService = Depends(Provide[Container.auth_service])
):
    user = await auth_service.authenticate_user(payload.email, payload.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password!",
            headers={"WWW-Authenticate": "Bearer"},
        )

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