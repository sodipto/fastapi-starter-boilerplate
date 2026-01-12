import uuid
from fastapi import APIRouter, Depends
from dependency_injector.wiring import inject, Provide

from app.core.container import Container
from app.schema.request.auth.login import LoginRequest
from app.schema.request.auth.refresh_token import TokenRefreshRequest
from app.schema.response.auth import AuthResponse
from app.services.auth_service import AuthService
from app.services.interfaces.auth_service_interface import IAuthService

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post("/login", summary="Login with email and password", response_model=AuthResponse)
@inject
async def login(
    payload: LoginRequest,
    auth_service: IAuthService = Depends(Provide[Container.auth_service])
):
    return await auth_service.login(payload.email, payload.password)


@router.post("/refresh-token", summary="Refresh access and refresh token", response_model=AuthResponse)
@inject
async def refresh_token(
    payload: TokenRefreshRequest,
    auth_service: IAuthService = Depends(Provide[Container.auth_service])
):
    """
    Refresh access and refresh tokens.
    
    This endpoint validates the current tokens and generates new ones if valid.
    The refresh token must not be expired and must match the one stored in the database.
    
    - **access_token**: Current access token (may be expired)
    - **refresh_token**: Current refresh token (must be valid)
    
    Returns:
    - **tokenInfo**: New access and refresh tokens with expiry times
    - **userInfo**: User profile information
    """
    return await auth_service.refresh_token(payload.access_token, payload.refresh_token)