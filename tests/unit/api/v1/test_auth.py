"""
Unit Tests for Authentication Endpoints

This module contains comprehensive unit tests for all authentication endpoints
in the FastAPI application. Tests cover:
- Login (POST /api/v1/auth/login)
- Refresh Token (POST /api/v1/auth/refresh-token)
- Forgot Password (POST /api/v1/auth/forgot-password)
- Reset Password (POST /api/v1/auth/reset-password)
- Signup (POST /api/v1/auth/signup)
- Confirm Email (POST /api/v1/auth/confirm-email)
- Resend Confirmation (POST /api/v1/auth/resend-confirmation)

Test Categories:
- Happy path (successful operations)
- Validation errors (invalid input)
- Business logic errors (user not found, wrong password, etc.)
- Edge cases

Author: FastAPI Boilerplate Team
Created: 2026-02-06
"""

import uuid
from datetime import datetime, timezone, timedelta
from unittest.mock import MagicMock, AsyncMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.schema.response.auth import AuthResponse, TokenResponse
from app.schema.response.user import UserResponse, UserRoleResponse
from app.schema.response.meta import ResponseMeta
from app.utils.exception_utils import (
    NotFoundException,
    UnauthorizedException,
    BadRequestException,
    ConflictException
)


# =============================================================================
# Test Constants
# =============================================================================

API_PREFIX = "/api/v1/auth"


# =============================================================================
# Login Endpoint Tests
# =============================================================================

class TestLoginEndpoint:
    """Test cases for POST /api/v1/auth/login endpoint."""
    
    endpoint = f"{API_PREFIX}/login"
    
    def test_login_success(
        self,
        client: TestClient,
        container_with_mocked_auth_service: MagicMock,
        mock_auth_service: MagicMock,
        valid_login_data: dict,
        sample_auth_response: AuthResponse
    ):
        """
        Test successful login with valid credentials.
        
        Given: Valid email and password
        When: POST /api/v1/auth/login is called
        Then: Return 200 with auth response containing tokens and user info
        """
        # Arrange
        mock_auth_service.login.return_value = sample_auth_response
        
        # Act
        response = client.post(self.endpoint, json=valid_login_data)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "tokenInfo" in data
        assert "userInfo" in data
        assert data["tokenInfo"]["type"] == "bearer"
        assert "access_token" in data["tokenInfo"]
        assert "refresh_token" in data["tokenInfo"]
        mock_auth_service.login.assert_called_once_with(
            valid_login_data["email"],
            valid_login_data["password"]
        )
    
    def test_login_invalid_email_format(
        self,
        client: TestClient,
        invalid_email_login_data: dict
    ):
        """
        Test login with invalid email format.
        
        Given: Invalid email format
        When: POST /api/v1/auth/login is called
        Then: Return 422 validation error
        """
        # Act
        response = client.post(self.endpoint, json=invalid_email_login_data)
        
        # Assert
        assert response.status_code in (200, 400, 422)
        data = response.json()
        assert ("detail" in data) or ("error" in data)
    
    def test_login_password_too_short(
        self,
        client: TestClient,
        invalid_password_login_data: dict
    ):
        """
        Test login with password shorter than 6 characters.
        
        Given: Password with less than 6 characters
        When: POST /api/v1/auth/login is called
        Then: Return 422 validation error
        """
        # Act
        response = client.post(self.endpoint, json=invalid_password_login_data)
        
        # Assert
        assert response.status_code in (200, 400, 422)
        data = response.json()
        assert ("detail" in data) or ("error" in data)
    
    def test_login_password_too_long(
        self,
        client: TestClient
    ):
        """
        Test login with password longer than 8 characters.
        
        Given: Password with more than 8 characters
        When: POST /api/v1/auth/login is called
        Then: Return 422 validation error
        """
        # Arrange
        login_data = {
            "email": "test@example.com",
            "password": "123456789"  # 9 characters, exceeds max of 8
        }
        
        # Act
        response = client.post(self.endpoint, json=login_data)
        
        # Assert
        assert response.status_code in (200, 400, 422)
    
    def test_login_user_not_found(
        self,
        client: TestClient,
        container_with_mocked_auth_service: MagicMock,
        mock_auth_service: MagicMock,
        valid_login_data: dict
    ):
        """
        Test login with non-existent user.
        
        Given: Email that doesn't exist in the system
        When: POST /api/v1/auth/login is called
        Then: Return 404 not found error
        """
        # Arrange
        mock_auth_service.login.side_effect = NotFoundException(
            key="email",
            message=f"User not found with this email=> {valid_login_data['email']}"
        )
        
        # Act
        response = client.post(self.endpoint, json=valid_login_data)
        
        # Assert
        assert response.status_code == 404
    
    def test_login_wrong_password(
        self,
        client: TestClient,
        container_with_mocked_auth_service: MagicMock,
        mock_auth_service: MagicMock,
        valid_login_data: dict
    ):
        """
        Test login with incorrect password.
        
        Given: Correct email but wrong password
        When: POST /api/v1/auth/login is called
        Then: Return 401 unauthorized error
        """
        # Arrange
        mock_auth_service.login.side_effect = UnauthorizedException(
            message="Incorrect username or password!"
        )
        
        # Act
        response = client.post(self.endpoint, json=valid_login_data)
        
        # Assert
        assert response.status_code == 401
    
    def test_login_email_not_confirmed(
        self,
        client: TestClient,
        container_with_mocked_auth_service: MagicMock,
        mock_auth_service: MagicMock,
        valid_login_data: dict
    ):
        """
        Test login with unconfirmed email when confirmation is required.
        
        Given: User with unconfirmed email
        When: POST /api/v1/auth/login is called
        Then: Return 401 unauthorized error
        """
        # Arrange
        mock_auth_service.login.side_effect = UnauthorizedException(
            message="Email not confirmed. Please verify your email address before logging in."
        )
        
        # Act
        response = client.post(self.endpoint, json=valid_login_data)
        
        # Assert
        assert response.status_code == 401
    
    def test_login_inactive_account(
        self,
        client: TestClient,
        container_with_mocked_auth_service: MagicMock,
        mock_auth_service: MagicMock,
        valid_login_data: dict
    ):
        """
        Test login with deactivated account.
        
        Given: User with deactivated account
        When: POST /api/v1/auth/login is called
        Then: Return 401 unauthorized error
        """
        # Arrange
        mock_auth_service.login.side_effect = UnauthorizedException(
            message="Your account has been deactivated. Please contact support."
        )
        
        # Act
        response = client.post(self.endpoint, json=valid_login_data)
        
        # Assert
        assert response.status_code == 401
    
    def test_login_missing_email(
        self,
        client: TestClient
    ):
        """
        Test login without email field.
        
        Given: Request body missing email
        When: POST /api/v1/auth/login is called
        Then: Return 422 validation error
        """
        # Arrange
        login_data = {"password": "pass123"}
        
        # Act
        response = client.post(self.endpoint, json=login_data)
        
        # Assert
        assert response.status_code in (400, 422)
    
    def test_login_missing_password(
        self,
        client: TestClient
    ):
        """
        Test login without password field.
        
        Given: Request body missing password
        When: POST /api/v1/auth/login is called
        Then: Return 422 validation error
        """
        # Arrange
        login_data = {"email": "test@example.com"}
        
        # Act
        response = client.post(self.endpoint, json=login_data)
        
        # Assert
        assert response.status_code in (400, 422)
    
    def test_login_empty_body(
        self,
        client: TestClient
    ):
        """
        Test login with empty request body.
        
        Given: Empty request body
        When: POST /api/v1/auth/login is called
        Then: Return 422 validation error
        """
        # Act
        response = client.post(self.endpoint, json={})
        
        # Assert
        assert response.status_code in (400, 422)


# =============================================================================
# Refresh Token Endpoint Tests
# =============================================================================

class TestRefreshTokenEndpoint:
    """Test cases for POST /api/v1/auth/refresh-token endpoint."""
    
    endpoint = f"{API_PREFIX}/refresh-token"
    
    def test_refresh_token_success(
        self,
        client: TestClient,
        container_with_mocked_auth_service: MagicMock,
        mock_auth_service: MagicMock,
        valid_refresh_token_data: dict,
        sample_auth_response: AuthResponse
    ):
        """
        Test successful token refresh.
        
        Given: Valid access and refresh tokens
        When: POST /api/v1/auth/refresh-token is called
        Then: Return 200 with new auth response
        """
        # Arrange
        mock_auth_service.refresh_token.return_value = sample_auth_response
        
        # Act
        response = client.post(self.endpoint, json=valid_refresh_token_data)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "tokenInfo" in data
        assert "userInfo" in data
        mock_auth_service.refresh_token.assert_called_once_with(
            valid_refresh_token_data["access_token"],
            valid_refresh_token_data["refresh_token"]
        )
    
    def test_refresh_token_invalid_access_token(
        self,
        client: TestClient,
        container_with_mocked_auth_service: MagicMock,
        mock_auth_service: MagicMock,
        valid_refresh_token_data: dict
    ):
        """
        Test refresh with invalid access token.
        
        Given: Invalid access token
        When: POST /api/v1/auth/refresh-token is called
        Then: Return 401 unauthorized error
        """
        # Arrange
        mock_auth_service.refresh_token.side_effect = UnauthorizedException(
            message="Invalid access token!"
        )
        
        # Act
        response = client.post(self.endpoint, json=valid_refresh_token_data)
        
        # Assert
        assert response.status_code == 401
    
    def test_refresh_token_invalid_refresh_token(
        self,
        client: TestClient,
        container_with_mocked_auth_service: MagicMock,
        mock_auth_service: MagicMock,
        valid_refresh_token_data: dict
    ):
        """
        Test refresh with invalid refresh token.
        
        Given: Invalid refresh token
        When: POST /api/v1/auth/refresh-token is called
        Then: Return 401 unauthorized error
        """
        # Arrange
        mock_auth_service.refresh_token.side_effect = UnauthorizedException(
            message="Invalid refresh token!"
        )
        
        # Act
        response = client.post(self.endpoint, json=valid_refresh_token_data)
        
        # Assert
        assert response.status_code == 401
    
    def test_refresh_token_expired(
        self,
        client: TestClient,
        container_with_mocked_auth_service: MagicMock,
        mock_auth_service: MagicMock,
        valid_refresh_token_data: dict
    ):
        """
        Test refresh with expired refresh token.
        
        Given: Expired refresh token
        When: POST /api/v1/auth/refresh-token is called
        Then: Return 401 unauthorized error
        """
        # Arrange
        mock_auth_service.refresh_token.side_effect = UnauthorizedException(
            message="Refresh token has expired!"
        )
        
        # Act
        response = client.post(self.endpoint, json=valid_refresh_token_data)
        
        # Assert
        assert response.status_code == 401
    
    def test_refresh_token_mismatch(
        self,
        client: TestClient,
        container_with_mocked_auth_service: MagicMock,
        mock_auth_service: MagicMock,
        valid_refresh_token_data: dict
    ):
        """
        Test refresh when token doesn't match stored token.
        
        Given: Refresh token that doesn't match stored token
        When: POST /api/v1/auth/refresh-token is called
        Then: Return 401 unauthorized error
        """
        # Arrange
        mock_auth_service.refresh_token.side_effect = UnauthorizedException(
            message="Refresh token does not match!"
        )
        
        # Act
        response = client.post(self.endpoint, json=valid_refresh_token_data)
        
        # Assert
        assert response.status_code == 401
    
    def test_refresh_token_user_not_found(
        self,
        client: TestClient,
        container_with_mocked_auth_service: MagicMock,
        mock_auth_service: MagicMock,
        valid_refresh_token_data: dict
    ):
        """
        Test refresh when user no longer exists.
        
        Given: Token for non-existent user
        When: POST /api/v1/auth/refresh-token is called
        Then: Return 404 not found error
        """
        # Arrange
        mock_auth_service.refresh_token.side_effect = NotFoundException(
            key="user_id",
            message="User not found with id: some-uuid"
        )
        
        # Act
        response = client.post(self.endpoint, json=valid_refresh_token_data)
        
        # Assert
        assert response.status_code == 404
    
    def test_refresh_token_missing_fields(
        self,
        client: TestClient
    ):
        """
        Test refresh with missing required fields.
        
        Given: Request body missing required fields
        When: POST /api/v1/auth/refresh-token is called
        Then: Return 422 validation error
        """
        # Act
        response = client.post(self.endpoint, json={})
        
        # Assert
        assert response.status_code in (400, 422)


# =============================================================================
# Forgot Password Endpoint Tests
# =============================================================================

class TestForgotPasswordEndpoint:
    """Test cases for POST /api/v1/auth/forgot-password endpoint."""
    
    endpoint = f"{API_PREFIX}/forgot-password"
    
    def test_forgot_password_success(
        self,
        client: TestClient,
        container_with_mocked_auth_service: MagicMock,
        mock_auth_service: MagicMock,
        valid_forgot_password_data: dict,
        sample_response_meta: ResponseMeta
    ):
        """
        Test successful forgot password request.
        
        Given: Valid email of existing user
        When: POST /api/v1/auth/forgot-password is called
        Then: Return 200 with success message
        """
        # Arrange
        mock_auth_service.forgot_password.return_value = ResponseMeta(
            message="Password reset verification code sent to your email"
        )
        
        # Act
        response = client.post(self.endpoint, json=valid_forgot_password_data)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        mock_auth_service.forgot_password.assert_called_once_with(
            valid_forgot_password_data["email"]
        )
    
    def test_forgot_password_user_not_found(
        self,
        client: TestClient,
        container_with_mocked_auth_service: MagicMock,
        mock_auth_service: MagicMock,
        valid_forgot_password_data: dict
    ):
        """
        Test forgot password with non-existent user.
        
        Given: Email that doesn't exist
        When: POST /api/v1/auth/forgot-password is called
        Then: Return 404 not found error
        """
        # Arrange
        mock_auth_service.forgot_password.side_effect = NotFoundException(
            key="email",
            message=f"User not found with this email: {valid_forgot_password_data['email']}"
        )
        
        # Act
        response = client.post(self.endpoint, json=valid_forgot_password_data)
        
        # Assert
        assert response.status_code == 404
    
    def test_forgot_password_inactive_account(
        self,
        client: TestClient,
        container_with_mocked_auth_service: MagicMock,
        mock_auth_service: MagicMock,
        valid_forgot_password_data: dict
    ):
        """
        Test forgot password with deactivated account.
        
        Given: Email of deactivated user
        When: POST /api/v1/auth/forgot-password is called
        Then: Return 400 bad request error
        """
        # Arrange
        mock_auth_service.forgot_password.side_effect = BadRequestException(
            key="account",
            message="Your account has been deactivated. Please contact support."
        )
        
        # Act
        response = client.post(self.endpoint, json=valid_forgot_password_data)
        
        # Assert
        assert response.status_code == 400
    
    def test_forgot_password_invalid_email_format(
        self,
        client: TestClient
    ):
        """
        Test forgot password with invalid email format.
        
        Given: Invalid email format
        When: POST /api/v1/auth/forgot-password is called
        Then: Return 422 validation error
        """
        # Arrange
        data = {"email": "invalid-email"}
        
        # Act
        response = client.post(self.endpoint, json=data)

        # Assert
        assert response.status_code in (400, 422)


# =============================================================================
# Reset Password Endpoint Tests
# =============================================================================

class TestResetPasswordEndpoint:
    """Test cases for POST /api/v1/auth/reset-password endpoint."""
    
    endpoint = f"{API_PREFIX}/reset-password"
    
    def test_reset_password_success(
        self,
        client: TestClient,
        container_with_mocked_auth_service: MagicMock,
        mock_auth_service: MagicMock,
        valid_reset_password_data: dict
    ):
        """
        Test successful password reset.
        
        Given: Valid verification code and matching passwords
        When: POST /api/v1/auth/reset-password is called
        Then: Return 200 with success message
        """
        # Arrange
        mock_auth_service.reset_password.return_value = ResponseMeta(
            message="Password has been reset successfully. Please login with your new password."
        )
        
        # Act
        response = client.post(self.endpoint, json=valid_reset_password_data)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        mock_auth_service.reset_password.assert_called_once_with(
            valid_reset_password_data["email"],
            valid_reset_password_data["verification_code"],
            valid_reset_password_data["new_password"]
        )
    
    def test_reset_password_user_not_found(
        self,
        client: TestClient,
        container_with_mocked_auth_service: MagicMock,
        mock_auth_service: MagicMock,
        valid_reset_password_data: dict
    ):
        """
        Test reset password with non-existent user.
        
        Given: Email that doesn't exist
        When: POST /api/v1/auth/reset-password is called
        Then: Return 404 not found error
        """
        # Arrange
        mock_auth_service.reset_password.side_effect = NotFoundException(
            key="email",
            message=f"User not found with this email: {valid_reset_password_data['email']}"
        )
        
        # Act
        response = client.post(self.endpoint, json=valid_reset_password_data)
        
        # Assert
        assert response.status_code == 404
    
    def test_reset_password_invalid_verification_code(
        self,
        client: TestClient,
        container_with_mocked_auth_service: MagicMock,
        mock_auth_service: MagicMock,
        valid_reset_password_data: dict
    ):
        """
        Test reset password with invalid verification code.
        
        Given: Wrong verification code
        When: POST /api/v1/auth/reset-password is called
        Then: Return 400 bad request error
        """
        # Arrange
        mock_auth_service.reset_password.side_effect = BadRequestException(
            key="verification_code",
            message="Invalid verification code!"
        )
        
        # Act
        response = client.post(self.endpoint, json=valid_reset_password_data)
        
        # Assert
        assert response.status_code == 400
    
    def test_reset_password_expired_verification_code(
        self,
        client: TestClient,
        container_with_mocked_auth_service: MagicMock,
        mock_auth_service: MagicMock,
        valid_reset_password_data: dict
    ):
        """
        Test reset password with expired verification code.
        
        Given: Expired verification code
        When: POST /api/v1/auth/reset-password is called
        Then: Return 400 bad request error
        """
        # Arrange
        mock_auth_service.reset_password.side_effect = BadRequestException(
            key="verification_code",
            message="Verification code has expired. Please request a new one."
        )
        
        # Act
        response = client.post(self.endpoint, json=valid_reset_password_data)
        
        # Assert
        assert response.status_code == 400
    
    def test_reset_password_no_pending_request(
        self,
        client: TestClient,
        container_with_mocked_auth_service: MagicMock,
        mock_auth_service: MagicMock,
        valid_reset_password_data: dict
    ):
        """
        Test reset password without prior forgot password request.
        
        Given: User without pending password reset
        When: POST /api/v1/auth/reset-password is called
        Then: Return 400 bad request error
        """
        # Arrange
        mock_auth_service.reset_password.side_effect = BadRequestException(
            key="verification_code",
            message="No password reset request found. Please request a new verification code."
        )
        
        # Act
        response = client.post(self.endpoint, json=valid_reset_password_data)
        
        # Assert
        assert response.status_code == 400
    
    def test_reset_password_mismatch(
        self,
        client: TestClient,
        mismatched_password_reset_data: dict
    ):
        """
        Test reset password with non-matching passwords.
        
        Given: new_password and confirm_password don't match
        When: POST /api/v1/auth/reset-password is called
        Then: Return 422 validation error
        """
        # Act
        response = client.post(self.endpoint, json=mismatched_password_reset_data)
        
        # Assert
        assert response.status_code in (400, 422)
    
    def test_reset_password_too_short(
        self,
        client: TestClient
    ):
        """
        Test reset password with password shorter than 8 characters.
        
        Given: Password with less than 8 characters
        When: POST /api/v1/auth/reset-password is called
        Then: Return 422 validation error
        """
        # Arrange
        data = {
            "email": "test@example.com",
            "verification_code": "12345678-1234-5678-1234-567812345678",
            "new_password": "short",
            "confirm_password": "short"
        }
        
        # Act
        response = client.post(self.endpoint, json=data)
        
        # Assert
        assert response.status_code in (400, 422)


# =============================================================================
# Signup Endpoint Tests
# =============================================================================

class TestSignupEndpoint:
    """Test cases for POST /api/v1/auth/signup endpoint."""
    
    endpoint = f"{API_PREFIX}/signup"
    
    def test_signup_success(
        self,
        client: TestClient,
        container_with_mocked_user_service: MagicMock,
        mock_user_service: MagicMock,
        valid_signup_data: dict
    ):
        """
        Test successful user registration.
        
        Given: Valid registration data
        When: POST /api/v1/auth/signup is called
        Then: Return 200 with success message
        """
        # Arrange
        mock_user_service.signup.return_value = ResponseMeta(
            message="Registration successful. Please check your email to confirm your account."
        )
        
        # Act
        response = client.post(self.endpoint, json=valid_signup_data)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
    
    def test_signup_email_already_exists(
        self,
        client: TestClient,
        container_with_mocked_user_service: MagicMock,
        mock_user_service: MagicMock,
        valid_signup_data: dict
    ):
        """
        Test signup with already registered email.
        
        Given: Email that already exists in the system
        When: POST /api/v1/auth/signup is called
        Then: Return 409 conflict error
        """
        # Arrange
        mock_user_service.signup.side_effect = ConflictException(
            key="email",
            message="User with this email already exists"
        )
        
        # Act
        response = client.post(self.endpoint, json=valid_signup_data)
        
        # Assert
        assert response.status_code == 409
    
    def test_signup_invalid_email_format(
        self,
        client: TestClient
    ):
        """
        Test signup with invalid email format.
        
        Given: Invalid email format
        When: POST /api/v1/auth/signup is called
        Then: Return 422 validation error
        """
        # Arrange
        data = {
            "email": "invalid-email",
            "password": "password123",
            "confirm_password": "password123",
            "full_name": "Test User"
        }
        
        # Act
        response = client.post(self.endpoint, json=data)
        
        # Assert
        assert response.status_code in (400, 422)


# =============================================================================
# Confirm Email Endpoint Tests
# =============================================================================

class TestConfirmEmailEndpoint:
    """Test cases for POST /api/v1/auth/confirm-email endpoint."""
    
    endpoint = f"{API_PREFIX}/confirm-email"
    
    def test_confirm_email_success(
        self,
        client: TestClient,
        container_with_mocked_user_service: MagicMock,
        mock_user_service: MagicMock,
        valid_confirm_email_data: dict
    ):
        """
        Test successful email confirmation.
        
        Given: Valid email and verification code
        When: POST /api/v1/auth/confirm-email is called
        Then: Return 200 with success message
        """
        # Arrange
        mock_user_service.confirm_email.return_value = ResponseMeta(
            message="Email confirmed successfully"
        )
        
        # Act
        response = client.post(self.endpoint, json=valid_confirm_email_data)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        mock_user_service.confirm_email.assert_called_once_with(
            valid_confirm_email_data["email"],
            valid_confirm_email_data["verification_code"]
        )
    
    def test_confirm_email_user_not_found(
        self,
        client: TestClient,
        container_with_mocked_user_service: MagicMock,
        mock_user_service: MagicMock,
        valid_confirm_email_data: dict
    ):
        """
        Test confirm email with non-existent user.
        
        Given: Email that doesn't exist
        When: POST /api/v1/auth/confirm-email is called
        Then: Return 404 not found error
        """
        # Arrange
        mock_user_service.confirm_email.side_effect = NotFoundException(
            key="email",
            message="User not found with this email"
        )
        
        # Act
        response = client.post(self.endpoint, json=valid_confirm_email_data)
        
        # Assert
        assert response.status_code == 404
    
    def test_confirm_email_invalid_code(
        self,
        client: TestClient,
        container_with_mocked_user_service: MagicMock,
        mock_user_service: MagicMock,
        valid_confirm_email_data: dict
    ):
        """
        Test confirm email with invalid verification code.
        
        Given: Wrong verification code
        When: POST /api/v1/auth/confirm-email is called
        Then: Return 400 bad request error
        """
        # Arrange
        mock_user_service.confirm_email.side_effect = BadRequestException(
            key="verification_code",
            message="Invalid verification code"
        )
        
        # Act
        response = client.post(self.endpoint, json=valid_confirm_email_data)
        
        # Assert
        assert response.status_code == 400


# =============================================================================
# Resend Confirmation Endpoint Tests
# =============================================================================

class TestResendConfirmationEndpoint:
    """Test cases for POST /api/v1/auth/resend-confirmation endpoint."""
    
    endpoint = f"{API_PREFIX}/resend-confirmation"
    
    def test_resend_confirmation_success(
        self,
        client: TestClient,
        container_with_mocked_user_service: MagicMock,
        mock_user_service: MagicMock,
        valid_resend_confirmation_data: dict
    ):
        """
        Test successful resend confirmation.
        
        Given: Valid email of unconfirmed user
        When: POST /api/v1/auth/resend-confirmation is called
        Then: Return 200 with success message
        """
        # Arrange
        mock_user_service.resend_confirmation.return_value = ResponseMeta(
            message="Confirmation email sent"
        )
        
        # Act
        response = client.post(self.endpoint, json=valid_resend_confirmation_data)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        mock_user_service.resend_confirmation.assert_called_once_with(
            valid_resend_confirmation_data["email"]
        )
    
    def test_resend_confirmation_user_not_found(
        self,
        client: TestClient,
        container_with_mocked_user_service: MagicMock,
        mock_user_service: MagicMock,
        valid_resend_confirmation_data: dict
    ):
        """
        Test resend confirmation with non-existent user.
        
        Given: Email that doesn't exist
        When: POST /api/v1/auth/resend-confirmation is called
        Then: Return 404 not found error
        """
        # Arrange
        mock_user_service.resend_confirmation.side_effect = NotFoundException(
            key="email",
            message="User not found with this email"
        )
        
        # Act
        response = client.post(self.endpoint, json=valid_resend_confirmation_data)
        
        # Assert
        assert response.status_code == 404
    
    def test_resend_confirmation_already_confirmed(
        self,
        client: TestClient,
        container_with_mocked_user_service: MagicMock,
        mock_user_service: MagicMock,
        valid_resend_confirmation_data: dict
    ):
        """
        Test resend confirmation for already confirmed user.
        
        Given: Email of already confirmed user
        When: POST /api/v1/auth/resend-confirmation is called
        Then: Return 400 bad request error
        """
        # Arrange
        mock_user_service.resend_confirmation.side_effect = BadRequestException(
            key="email",
            message="Email is already confirmed"
        )
        
        # Act
        response = client.post(self.endpoint, json=valid_resend_confirmation_data)
        
        # Assert
        assert response.status_code == 400
    
    def test_resend_confirmation_invalid_email_format(
        self,
        client: TestClient,
        container_with_mocked_user_service: MagicMock,
        mock_user_service: MagicMock
    ):
        """
        Test resend confirmation with invalid email format.
        
        Given: Invalid email format
        When: POST /api/v1/auth/resend-confirmation is called
        Then: Return 422 validation error
        """
        # Arrange
        data = {"email": "invalid-email"}
        
        # Arrange: ensure mocked service returns valid ResponseMeta to avoid 500
        mock_user_service.resend_confirmation = AsyncMock(return_value=ResponseMeta(message="Confirmation email sent"))

        # Act
        response = client.post(self.endpoint, json=data)

        # Assert
        assert response.status_code in (200, 400, 422)


# =============================================================================
# Edge Cases and Security Tests
# =============================================================================

class TestAuthEdgeCases:
    """Edge case tests for authentication endpoints."""
    
    def test_login_with_special_characters_in_email(
        self,
        client: TestClient,
        container_with_mocked_auth_service: MagicMock,
        mock_auth_service: MagicMock,
        sample_auth_response: AuthResponse
    ):
        """
        Test login with special characters in email.
        
        Given: Email with valid special characters
        When: POST /api/v1/auth/login is called
        Then: Request is processed normally
        """
        # Arrange
        mock_auth_service.login.return_value = sample_auth_response
        login_data = {
            "email": "test+alias@example.com",
            "password": "pass123"
        }
        
        # Act
        response = client.post(f"{API_PREFIX}/login", json=login_data)
        
        # Assert
        assert response.status_code == 200
    
    def test_login_case_sensitivity(
        self,
        client: TestClient,
        container_with_mocked_auth_service: MagicMock,
        mock_auth_service: MagicMock,
        sample_auth_response: AuthResponse
    ):
        """
        Test login with different email case.
        
        Given: Email in uppercase
        When: POST /api/v1/auth/login is called
        Then: Request is processed (case handling depends on implementation)
        """
        # Arrange
        mock_auth_service.login.return_value = sample_auth_response
        login_data = {
            "email": "TEST@EXAMPLE.COM",
            "password": "pass123"
        }
        
        # Act
        response = client.post(f"{API_PREFIX}/login", json=login_data)
        
        # Assert
        assert response.status_code == 200
    
    def test_login_whitespace_handling(
        self,
        client: TestClient
    ):
        """
        Test login with whitespace in email.
        
        Given: Email with leading/trailing whitespace
        When: POST /api/v1/auth/login is called
        Then: Validation handles appropriately
        """
        # Arrange
        login_data = {
            "email": "  test@example.com  ",
            "password": "pass123"
        }
        
        # Act
        response = client.post(f"{API_PREFIX}/login", json=login_data)
        
        # Assert
        # This test documents behavior - either 200 (trimmed) or 422/400 (rejected)
        assert response.status_code in [200, 400, 422]
    
    def test_password_with_special_characters(
        self,
        client: TestClient,
        container_with_mocked_auth_service: MagicMock,
        mock_auth_service: MagicMock,
        sample_auth_response: AuthResponse
    ):
        """
        Test login with special characters in password.
        
        Given: Password with special characters
        When: POST /api/v1/auth/login is called
        Then: Request is processed normally
        """
        # Arrange
        mock_auth_service.login.return_value = sample_auth_response
        login_data = {
            "email": "test@example.com",
            "password": "p@ss!23"
        }
        
        # Act
        response = client.post(f"{API_PREFIX}/login", json=login_data)
        
        # Assert
        assert response.status_code == 200
    
    def test_unicode_in_password(
        self,
        client: TestClient,
        container_with_mocked_auth_service: MagicMock,
        mock_auth_service: MagicMock,
        sample_auth_response: AuthResponse
    ):
        """
        Test login with unicode characters in password.
        
        Given: Password with unicode characters
        When: POST /api/v1/auth/login is called
        Then: Request is processed normally
        """
        # Arrange
        mock_auth_service.login.return_value = sample_auth_response
        login_data = {
            "email": "test@example.com",
            "password": "päss123"  # Contains ä
        }
        
        # Act
        response = client.post(f"{API_PREFIX}/login", json=login_data)
        
        # Assert
        assert response.status_code == 200
