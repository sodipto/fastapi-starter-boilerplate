from typing import Dict, Optional

from app.repositories.user_repository import UserRepository
from app.services.token_service import ITokenService
from app.utils.auth_utils import verify_password
from app.utils.exception_utils import NotFoundException, UnauthorizedException
from app.schema.response.auth import AuthResponse, TokenResponse
from app.schema.response.user import UserResponse


class AuthService:
    """
    Authentication service handling user authentication and token generation.
    
    This service is kept thin and delegates token generation logic to TokenService.
    """

    def __init__(self, user_repository: UserRepository, token_service: ITokenService):
        self.user_repository = user_repository
        self.token_service = token_service

    async def authenticate_user(self, email: str, password: str) -> AuthResponse:
        # Verify user exists
        user = await self.user_repository.get_by_email(email)
        if not user:
            raise NotFoundException(
                key="email",
                message=f"User not found with this email=> {email}",
            )

        # Verify password
        if not verify_password(password, user.password):
            raise UnauthorizedException(
                message="Incorrect username or password!",
            )

        # Generate tokens
        token_response = self.token_service.create_token_response(user)

        # Update user's refresh token in database
        user.refresh_token = token_response.refresh_token
        user.refresh_token_expiry_time = token_response.refresh_token_expiry_time
        await self.user_repository.update(user)

        return AuthResponse(
            tokenInfo=token_response,
            userInfo=UserResponse(
                id=user.id,
                email=user.email,
                full_name=user.full_name,
            ),
        )
