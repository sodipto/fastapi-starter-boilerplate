"""
Pytest Configuration and Fixtures

This module provides shared fixtures for testing the FastAPI application.
It includes:
- Test client setup with mocked dependencies
- Mock fixtures for services and repositories
- Sample data fixtures for testing

Usage:
    Fixtures are automatically discovered by pytest.
    Import specific fixtures in test files as needed.
"""

import uuid
from datetime import datetime, timezone, timedelta
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport

# Application imports
# Ensure test run does not start background jobs or migrations
from app.core.config import settings
settings.BACKGROUND_JOBS_ENABLED = False
settings.DATABASE_ENABLED = False
settings.SEQ_ENABLED = False

from app.main import app as fastapi_app
from app.core.container import Container
from app.models.user import User
from app.models.role import Role
from app.models.user_role import UserRole
from app.schema.response.auth import TokenResponse, AuthResponse
from app.schema.response.user import UserResponse, UserRoleResponse
from app.schema.response.meta import ResponseMeta


# =============================================================================
# Application Fixtures
# =============================================================================

@pytest.fixture(scope="function")
def app() -> FastAPI:
    """
    Provide a fresh FastAPI application instance for each test.
    
    Returns:
        FastAPI: The application instance with test configuration.
    """
    return fastapi_app


@pytest.fixture(scope="function")
def client(app: FastAPI) -> Generator[TestClient, None, None]:
    """
    Provide a synchronous test client for the application.
    
    Args:
        app: The FastAPI application instance.
        
    Yields:
        TestClient: A synchronous test client for making HTTP requests.
    """
    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client


@pytest.fixture(scope="function")
async def async_client(app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    """
    Provide an asynchronous test client for the application.
    
    Args:
        app: The FastAPI application instance.
        
    Yields:
        AsyncClient: An async HTTP client for making requests.
    """
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver"
    ) as ac:
        yield ac


# =============================================================================
# Mock Service Fixtures
# =============================================================================

@pytest.fixture
def mock_auth_service() -> MagicMock:
    """
    Create a mock auth service with async methods.
    
    Returns:
        MagicMock: A mock auth service instance.
    """
    mock = MagicMock()
    mock.login = AsyncMock()
    mock.refresh_token = AsyncMock()
    mock.forgot_password = AsyncMock()
    mock.reset_password = AsyncMock()
    return mock


@pytest.fixture
def mock_user_service() -> MagicMock:
    """
    Create a mock user service with async methods.
    
    Returns:
        MagicMock: A mock user service instance.
    """
    mock = MagicMock()
    mock.signup = AsyncMock()
    mock.confirm_email = AsyncMock()
    mock.resend_confirmation = AsyncMock()
    return mock


@pytest.fixture
def mock_token_service() -> MagicMock:
    """
    Create a mock token service.
    
    Returns:
        MagicMock: A mock token service instance.
    """
    mock = MagicMock()
    mock.create_token_response = MagicMock()
    mock.get_user_id_from_access_token = MagicMock()
    mock.verify_refresh_token = MagicMock()
    return mock


@pytest.fixture
def mock_user_repository() -> MagicMock:
    """
    Create a mock user repository with async methods.
    
    Returns:
        MagicMock: A mock user repository instance.
    """
    mock = MagicMock()
    mock.get_by_email = AsyncMock()
    mock.get_by_email_with_roles = AsyncMock()
    mock.get_by_id = AsyncMock()
    mock.get_by_id_with_roles = AsyncMock()
    mock.create = AsyncMock()
    mock.update = AsyncMock()
    mock.delete = AsyncMock()
    return mock


@pytest.fixture
def mock_cache_service() -> MagicMock:
    """
    Create a mock cache service with async methods.
    
    Returns:
        MagicMock: A mock cache service instance.
    """
    mock = MagicMock()
    mock.get = AsyncMock()
    mock.set = AsyncMock()
    mock.delete = AsyncMock()
    return mock


@pytest.fixture
def mock_email_service() -> MagicMock:
    """
    Create a mock email service with async methods.
    
    Returns:
        MagicMock: A mock email service instance.
    """
    mock = MagicMock()
    mock.send_email_async = AsyncMock()
    return mock


@pytest.fixture
def mock_email_template_service() -> MagicMock:
    """
    Create a mock email template service.
    
    Returns:
        MagicMock: A mock email template service instance.
    """
    mock = MagicMock()
    mock.render = MagicMock(return_value="<html>Mocked Email</html>")
    return mock


# =============================================================================
# Sample Data Fixtures
# =============================================================================

@pytest.fixture
def sample_user_id() -> uuid.UUID:
    """
    Provide a consistent sample user ID for testing.
    
    Returns:
        uuid.UUID: A sample user UUID.
    """
    return uuid.UUID("12345678-1234-5678-1234-567812345678")


@pytest.fixture
def sample_role_id() -> uuid.UUID:
    """
    Provide a consistent sample role ID for testing.
    
    Returns:
        uuid.UUID: A sample role UUID.
    """
    return uuid.UUID("87654321-4321-8765-4321-876543210987")


@pytest.fixture
def sample_role(sample_role_id: uuid.UUID) -> Role:
    """
    Create a sample role for testing.
    
    Args:
        sample_role_id: The role's UUID.
        
    Returns:
        Role: A sample role instance.
    """
    role = MagicMock(spec=Role)
    role.id = sample_role_id
    role.name = "User"
    role.normalized_name = "USER"
    return role


@pytest.fixture
def sample_user_role(sample_user_id: uuid.UUID, sample_role: Role) -> UserRole:
    """
    Create a sample user-role association for testing.
    
    Args:
        sample_user_id: The user's UUID.
        sample_role: The role to associate.
        
    Returns:
        UserRole: A sample user-role instance.
    """
    user_role = MagicMock(spec=UserRole)
    user_role.user_id = sample_user_id
    user_role.role_id = sample_role.id
    user_role.role = sample_role
    return user_role


@pytest.fixture
def sample_user(sample_user_id: uuid.UUID, sample_user_role: UserRole) -> User:
    """
    Create a sample user for testing.
    
    Args:
        sample_user_id: The user's UUID.
        sample_user_role: The user's role association.
        
    Returns:
        User: A sample user instance with roles.
    """
    user = MagicMock(spec=User)
    user.id = sample_user_id
    user.email = "test@example.com"
    user.full_name = "Test User"
    user.password = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.Aa..UVAWl2Wd4m"  # "password123"
    user.phone_number = "+1234567890"
    user.profile_image_url = None
    user.is_active = True
    user.email_confirmed = True
    user.refresh_token = None
    user.refresh_token_expiry_time = None
    user.forgot_password_verification_code = None
    user.forgot_password_verification_code_expiry_time = None
    user.roles = [sample_user_role]
    return user


@pytest.fixture
def sample_inactive_user(sample_user: User) -> User:
    """
    Create a sample inactive user for testing.
    
    Args:
        sample_user: The base user to modify.
        
    Returns:
        User: A sample inactive user instance.
    """
    sample_user.is_active = False
    return sample_user


@pytest.fixture
def sample_unconfirmed_user(sample_user: User) -> User:
    """
    Create a sample user with unconfirmed email for testing.
    
    Args:
        sample_user: The base user to modify.
        
    Returns:
        User: A sample user with unconfirmed email.
    """
    sample_user.email_confirmed = False
    return sample_user


@pytest.fixture
def sample_token_response() -> TokenResponse:
    """
    Create a sample token response for testing.
    
    Returns:
        TokenResponse: A sample token response with access and refresh tokens.
    """
    return TokenResponse(
        type="bearer",
        access_token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiMTIzNDU2NzgtMTIzNC01Njc4LTEyMzQtNTY3ODEyMzQ1Njc4IiwiZW1haWwiOiJ0ZXN0QGV4YW1wbGUuY29tIiwiZXhwIjoxNzA3MjM0NTY3LCJpYXQiOjE3MDcyMzA5NjcsInR5cGUiOiJhY2Nlc3MifQ.test",
        access_token_expiry_time=datetime.now(timezone.utc) + timedelta(minutes=30),
        refresh_token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiMTIzNDU2NzgtMTIzNC01Njc4LTEyMzQtNTY3ODEyMzQ1Njc4IiwiZXhwIjoxNzA3ODM1NzY3LCJpYXQiOjE3MDcyMzA5NjcsInR5cGUiOiJyZWZyZXNoIn0.test",
        refresh_token_expiry_time=datetime.now(timezone.utc) + timedelta(days=7)
    )


@pytest.fixture
def sample_user_response(sample_user_id: uuid.UUID, sample_role_id: uuid.UUID) -> UserResponse:
    """
    Create a sample user response for testing.
    
    Args:
        sample_user_id: The user's UUID.
        sample_role_id: The role's UUID.
        
    Returns:
        UserResponse: A sample user response instance.
    """
    return UserResponse(
        id=sample_user_id,
        email="test@example.com",
        full_name="Test User",
        phone_number="+1234567890",
        profile_image_url=None,
        is_active=True,
        email_confirmed=True,
        roles=[
            UserRoleResponse(
                id=sample_role_id,
                name="User",
                normalized_name="USER"
            )
        ]
    )


@pytest.fixture
def sample_auth_response(
    sample_token_response: TokenResponse,
    sample_user_response: UserResponse
) -> AuthResponse:
    """
    Create a sample auth response for testing.
    
    Args:
        sample_token_response: The token response to include.
        sample_user_response: The user response to include.
        
    Returns:
        AuthResponse: A complete auth response instance.
    """
    return AuthResponse(
        tokenInfo=sample_token_response,
        userInfo=sample_user_response
    )


@pytest.fixture
def sample_response_meta() -> ResponseMeta:
    """
    Create a sample response meta for testing.
    
    Returns:
        ResponseMeta: A sample response meta instance.
    """
    return ResponseMeta(message="Operation successful")


# =============================================================================
# Request Data Fixtures
# =============================================================================

@pytest.fixture
def valid_login_data() -> dict:
    """
    Provide valid login request data.
    
    Returns:
        dict: Valid login credentials.
    """
    return {
        "email": "test@example.com",
        "password": "pass123"
    }


@pytest.fixture
def invalid_email_login_data() -> dict:
    """
    Provide login data with invalid email format.
    
    Returns:
        dict: Login data with malformed email.
    """
    return {
        "email": "invalid-email",
        "password": "pass123"
    }


@pytest.fixture
def invalid_password_login_data() -> dict:
    """
    Provide login data with invalid password.
    
    Returns:
        dict: Login data with password too short.
    """
    return {
        "email": "test@example.com",
        "password": "12345"  # Less than 6 characters
    }


@pytest.fixture
def valid_refresh_token_data() -> dict:
    """
    Provide valid refresh token request data.
    
    Returns:
        dict: Valid access and refresh tokens.
    """
    return {
        "access_token": "valid.access.token",
        "refresh_token": "valid.refresh.token"
    }


@pytest.fixture
def valid_forgot_password_data() -> dict:
    """
    Provide valid forgot password request data.
    
    Returns:
        dict: Valid email for password reset.
    """
    return {
        "email": "test@example.com"
    }


@pytest.fixture
def valid_reset_password_data() -> dict:
    """
    Provide valid reset password request data.
    
    Returns:
        dict: Valid reset password data with matching passwords.
    """
    return {
        "email": "test@example.com",
        "verification_code": "12345678-1234-5678-1234-567812345678",
        "new_password": "newpassword1",
        "confirm_password": "newpassword1"
    }


@pytest.fixture
def mismatched_password_reset_data() -> dict:
    """
    Provide reset password data with mismatched passwords.
    
    Returns:
        dict: Reset password data where passwords don't match.
    """
    return {
        "email": "test@example.com",
        "verification_code": "12345678-1234-5678-1234-567812345678",
        "new_password": "newpassword1",
        "confirm_password": "different12"
    }


@pytest.fixture
def valid_signup_data() -> dict:
    """
    Provide valid signup request data.
    
    Returns:
        dict: Valid user registration data.
    """
    return {
        "email": "newuser@example.com",
        "password": "password123",
        "confirm_password": "password123",
        "full_name": "New User",
        "phone_number": "+1234567890"
    }


@pytest.fixture
def valid_confirm_email_data() -> dict:
    """
    Provide valid confirm email request data.
    
    Returns:
        dict: Valid email confirmation data.
    """
    return {
        "email": "test@example.com",
        "verification_code": "12345678-1234-5678-1234-567812345678"
    }


@pytest.fixture
def valid_resend_confirmation_data() -> dict:
    """
    Provide valid resend confirmation request data.
    
    Returns:
        dict: Valid email for resending confirmation.
    """
    return {
        "email": "test@example.com"
    }


# =============================================================================
# Container Override Fixtures
# =============================================================================

@pytest.fixture
def container_with_mocked_auth_service(
    app: FastAPI,
    mock_auth_service: MagicMock
) -> Generator[Container, None, None]:
    """
    Override the container's auth service with a mock.
    
    Args:
        app: The FastAPI application instance.
        mock_auth_service: The mock auth service to inject.
        
    Yields:
        Container: The container with overridden auth service.
    """
    container = app.container
    with container.auth_service.override(mock_auth_service):
        yield container


@pytest.fixture
def container_with_mocked_user_service(
    app: FastAPI,
    mock_user_service: MagicMock
) -> Generator[Container, None, None]:
    """
    Override the container's user service with a mock.
    
    Args:
        app: The FastAPI application instance.
        mock_user_service: The mock user service to inject.
        
    Yields:
        Container: The container with overridden user service.
    """
    container = app.container
    with container.user_service.override(mock_user_service):
        yield container


@pytest.fixture
def container_with_all_mocked_services(
    app: FastAPI,
    mock_auth_service: MagicMock,
    mock_user_service: MagicMock
) -> Generator[Container, None, None]:
    """
    Override the container with all mocked auth-related services.
    
    Args:
        app: The FastAPI application instance.
        mock_auth_service: The mock auth service.
        mock_user_service: The mock user service.
        
    Yields:
        Container: The container with all services mocked.
    """
    container = app.container
    with container.auth_service.override(mock_auth_service):
        with container.user_service.override(mock_user_service):
            yield container
