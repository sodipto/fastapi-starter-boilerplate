# Authentication

JWT-based authentication with refresh tokens and email verification.

## Table of Contents

- [Overview](#overview)
- [Configuration](#configuration)
- [Endpoints](#endpoints)
- [Signup Flow](#signup-flow)
- [Password Reset](#password-reset)
- [Protecting Routes](#protecting-routes)

---

## Overview

The authentication system provides:

- JWT access tokens (short-lived)
- Refresh tokens (long-lived)
- Email verification for new accounts
- Password reset via email
- Role assignment on signup

---

## Configuration

```env
# JWT Settings
SECRET_KEY=your-secret-key-min-32-characters
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# Email Verification
REQUIRE_EMAIL_CONFIRMED_ACCOUNT=True
EMAIL_VERIFICATION_CODE_EXPIRE_MINUTES=60

# Frontend URL (for email links)
FRONTEND_URL=http://localhost:3000
```

---

## Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/signup` | Register new user |
| POST | `/api/v1/auth/login` | Get access + refresh tokens |
| POST | `/api/v1/auth/refresh-token` | Refresh access token |
| POST | `/api/v1/auth/confirm-email` | Verify email address |
| POST | `/api/v1/auth/resend-confirmation` | Resend verification email |
| POST | `/api/v1/auth/forgot-password` | Request password reset |
| POST | `/api/v1/auth/reset-password` | Reset password with code |

---

## Signup Flow

### 1. User Registers

```http
POST /api/v1/auth/signup
Content-Type: application/json

{
  "email": "user@example.com",
  "full_name": "John Doe",
  "phone_number": "+1234567890",
  "password": "SecurePassword123!",
  "confirm_password": "SecurePassword123!"
}
```

### 2. System Actions

1. Create user with `CUSTOMER` role
2. If `REQUIRE_EMAIL_CONFIRMED_ACCOUNT=True`:
   - Generate verification code
   - Send confirmation email
3. Return success response

### 3. Email Confirmation

```http
POST /api/v1/auth/confirm-email
Content-Type: application/json

{
  "email": "user@example.com",
  "code": "123456"
}
```

### 4. Resend Confirmation

```http
POST /api/v1/auth/resend-confirmation
Content-Type: application/json

{
  "email": "user@example.com"
}
```

---

## Password Reset

### 1. Request Reset

```http
POST /api/v1/auth/forgot-password
Content-Type: application/json

{
  "email": "user@example.com"
}
```

User receives email with reset link/code.

### 2. Reset Password

```http
POST /api/v1/auth/reset-password
Content-Type: application/json

{
  "email": "user@example.com",
  "code": "abc123",
  "new_password": "NewSecurePassword123!",
  "confirm_password": "NewSecurePassword123!"
}
```

---

## Protecting Routes

### JWT Bearer Dependency

```python
from app.core.jwt_security import JWTBearer

@router.get("/protected")
async def protected_route(
    token_data = Depends(JWTBearer())
):
    return {"user_id": token_data.user_id}
```

### With Permission Check

```python
from app.core.rbac import AppPermissions, require_permission

@router.get(
    "/admin-only",
    dependencies=[Depends(require_permission(AppPermissions.USERS_VIEW))]
)
async def admin_route():
    return {"message": "Admin access granted"}
```

---

## Token Response

```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 900
}
```

### Access Token Payload

```json
{
  "sub": "user-uuid",
  "email": "user@example.com",
  "exp": 1700000000,
  "type": "access"
}
```

### Refresh Token Payload

```json
{
  "sub": "user-uuid",
  "exp": 1700604800,
  "type": "refresh"
}
```

---

## Email Templates

Templates are in `app/templates/emails/`:

| Template | Purpose |
|----------|---------|
| `confirm_email.html` | Email verification |
| `reset_password.html` | Password reset link |

Variables available:

```python
{
    "user_name": "John Doe",
    "verification_code": "123456",
    "reset_link": "https://app.com/reset?code=abc",
    "frontend_url": "https://app.com",
    "expire_minutes": 60
}
```
