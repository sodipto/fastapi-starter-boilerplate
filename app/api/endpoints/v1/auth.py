import uuid
from fastapi import APIRouter, Depends
from dependency_injector.wiring import inject, Provide

from app.core.container import Container
from app.schema.request.auth.login import LoginRequest
from app.schema.response.auth import AuthResponse
from app.services.auth_service import AuthService
from app.utils.auth_utils import create_access_token

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post("/login", summary="Login with email and password", response_model=AuthResponse)
@inject
async def login(
    payload: LoginRequest,
    auth_service: AuthService = Depends(Provide[Container.auth_service])
):
    return await auth_service.authenticate_user(payload.email, payload.password)