from datetime import datetime, timezone

from app.repositories.user_repository import UserRepository
from app.services.interfaces.i_token_service import ITokenService
from app.utils.auth_utils import verify_password
from app.utils.exception_utils import NotFoundException, UnauthorizedException
from app.schema.response.auth import AuthResponse
from app.schema.response.user import UserResponse


class AuthService:

    def __init__(self, user_repository: UserRepository, token_service: ITokenService):
        self.user_repository = user_repository
        self.token_service = token_service

    async def login(self, email: str, password: str) -> AuthResponse:
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

    async def refresh_token(self, access_token: str, refresh_token: str) -> AuthResponse:
        # Extract user_id from access token
        user_id = self.token_service.get_user_id_from_access_token(access_token)
        if not user_id:
            raise UnauthorizedException(message="Invalid access token!")

        # Fetch user from database
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise NotFoundException(
                key="user_id",
                message=f"User not found with id: {user_id}"
            )

        # Verify refresh token
        refresh_payload = self.token_service.verify_refresh_token(refresh_token)
        if not refresh_payload:
            raise UnauthorizedException(message="Invalid refresh token!")

        # Verify refresh token matches stored token
        if user.refresh_token != refresh_token:
            raise UnauthorizedException(message="Refresh token does not match!")

        # Check if refresh token is expired
        if user.refresh_token_expiry_time < datetime.now(timezone.utc):
            raise UnauthorizedException(message="Refresh token has expired!")

        # Generate new tokens
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
