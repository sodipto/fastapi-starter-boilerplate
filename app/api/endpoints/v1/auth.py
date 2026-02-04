import uuid
from fastapi import APIRouter, Depends
from dependency_injector.wiring import inject, Provide

from app.core.container import Container
from app.schema.request.auth.login import LoginRequest
from app.schema.request.auth.signup import SignupRequest
from app.schema.request.auth.confirm_email import ConfirmEmailRequest
from app.schema.request.auth.resend_confirmation import ResendConfirmationRequest
from app.schema.request.auth.refresh_token import TokenRefreshRequest
from app.schema.request.auth.forgot_password import ForgotPasswordRequest
from app.schema.request.auth.reset_password import ResetPasswordRequest
from app.schema.response.auth import AuthResponse
from app.schema.response.meta import ResponseMeta
from app.services.interfaces.auth_service_interface import IAuthService
from app.services.interfaces.user_service_interface import IUserService
from app.schema.response.meta import ResponseMeta

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


@router.post("/forgot-password", summary="Request password reset verification code", response_model=ResponseMeta)
@inject
async def forgot_password(
    payload: ForgotPasswordRequest,
    auth_service: IAuthService = Depends(Provide[Container.auth_service])
):
    """
    Request a password reset verification code.
    
    Sends a verification code to the user's email address that can be used to reset their password.
    The code expires in 15 minutes.
    
    - **email**: Email address of the account to reset
    
    Returns:
    - **message**: Confirmation that the verification code was sent
    """
    return await auth_service.forgot_password(payload.email)


@router.post("/signup", summary="Create a new user account", response_model=ResponseMeta)
@inject
async def signup(
    payload: SignupRequest,
    user_service: IUserService = Depends(Provide[Container.user_service])
):
    """Register a new user and send confirmation email."""
    return await user_service.signup(payload)


@router.post("/confirm-email", summary="Confirm email address", response_model=ResponseMeta)
@inject
async def confirm_email(
    payload: ConfirmEmailRequest,
    user_service: IUserService = Depends(Provide[Container.user_service])
):
    return await user_service.confirm_email(payload.email, payload.verification_code)


@router.post("/resend-confirmation", summary="Resend email confirmation", response_model=ResponseMeta)
@inject
async def resend_confirmation(
    payload: ResendConfirmationRequest,
    user_service: IUserService = Depends(Provide[Container.user_service])
):
    return await user_service.resend_confirmation(payload.email)


@router.post("/reset-password", summary="Reset password using verification code", response_model=ResponseMeta)
@inject
async def reset_password(
    payload: ResetPasswordRequest,
    auth_service: IAuthService = Depends(Provide[Container.auth_service])
):
    """
    Reset password using the verification code sent to email.
    
    Uses the verification code from the forgot-password endpoint to set a new password.
    The verification code must be valid and not expired.
    
    - **email**: Email address of the account
    - **verification_code**: Code sent to email (UUID format)
    - **new_password**: New password (minimum 6 characters)
    
    Returns:
    - **message**: Confirmation that the password was reset successfully
    """
    return await auth_service.reset_password(
        payload.email,
        payload.verification_code,
        payload.new_password
    )