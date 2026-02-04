# Exception Handling

Centralized error handling with custom exceptions, middleware, and consistent API responses.

## Table of Contents

- [Overview](#overview)
- [Error Response Format](#error-response-format)
- [Custom Exceptions](#custom-exceptions)
- [Using Exceptions](#using-exceptions)
- [Validation Errors](#validation-errors)
- [Middleware Configuration](#middleware-configuration)
- [Logging](#logging)

---

## Overview

The exception system provides:

- **Consistent error responses** across all endpoints
- **Custom exceptions** for common HTTP errors (400, 401, 403, 404, 409, 500)
- **Automatic logging** with correlation IDs
- **Validation error handling** for Pydantic schemas
- **Structured properties** for Seq integration

---

## Error Response Format

All errors return a consistent JSON structure:

```json
{
  "error": {
    "logId": "550e8400-e29b-41d4-a716-446655440000",
    "statusCode": 400,
    "type": "BadRequestException",
    "messages": {
      "email": "Invalid email format"
    }
  }
}
```

| Field | Description |
|-------|-------------|
| `logId` | Unique correlation ID for tracing |
| `statusCode` | HTTP status code |
| `type` | Exception type name |
| `messages` | Key-value pairs of field/error messages |

### Response Schema

```python
# app/schema/response/error.py
from pydantic import BaseModel
from typing import Dict

class ErrorBody(BaseModel):
    logId: str
    statusCode: int
    type: str
    messages: Dict[str, str]

class ErrorResponse(BaseModel):
    error: ErrorBody
```

---

## Custom Exceptions

All exceptions are defined in `app/utils/exception_utils.py`:

### BadRequestException (400)

Invalid input or business rule violation.

```python
from app.utils.exception_utils import BadRequestException

raise BadRequestException(
    key="email",
    message="Email already exists"
)
```

### UnauthorizedException (401)

Missing or invalid authentication.

```python
from app.utils.exception_utils import UnauthorizedException

raise UnauthorizedException(
    message="Invalid or expired token"
)
```

### ForbiddenException (403)

Authenticated but not authorized.

```python
from app.utils.exception_utils import ForbiddenException

raise ForbiddenException(
    key="permission",
    message="You do not have permission to access this resource"
)
```

### NotFoundException (404)

Resource not found.

```python
from app.utils.exception_utils import NotFoundException

raise NotFoundException(
    key="user",
    message="User not found with ID: 123"
)
```

### ConflictException (409)

Resource conflict (duplicate, version mismatch).

```python
from app.utils.exception_utils import ConflictException

raise ConflictException(
    key="email",
    message="A user with this email already exists"
)
```

---

## Using Exceptions

### In Services

```python
from app.utils.exception_utils import NotFoundException, ConflictException, BadRequestException

class UserService:
    async def get_user(self, user_id: UUID) -> User:
        user = await self._user_repository.get_by_id(user_id)
        if not user:
            raise NotFoundException(
                key="user",
                message=f"User not found with ID: {user_id}"
            )
        return user

    async def create_user(self, data: CreateUserRequest) -> User:
        existing = await self._user_repository.get_by_email(data.email)
        if existing:
            raise ConflictException(
                key="email",
                message="Email already registered"
            )
        # Create user...

    async def verify_email(self, email: str, code: str) -> None:
        user = await self._user_repository.get_by_email(email)
        if not user:
            raise NotFoundException(key="email", message="User not found")
        
        if user.email_verified:
            raise BadRequestException(
                key="email",
                message="Email already verified"
            )
        
        if user.verification_code != code:
            raise BadRequestException(
                key="code",
                message="Invalid verification code"
            )
```

### In Endpoints

Exceptions bubble up automatically—no try/catch needed:

```python
@router.get("/users/{user_id}")
async def get_user(
    user_id: UUID,
    user_service: IUserService = Depends(Provide[Container.user_service])
):
    # NotFoundException automatically returns 404 response
    return await user_service.get_user(user_id)
```

### In RBAC Dependencies

```python
from app.utils.exception_utils import ForbiddenException

async def require_permission(permission: PermissionDefinition):
    async def dependency(user_id: UUID = Depends(get_current_user_id)):
        has_permission = await permission_service.check_permission(user_id, permission)
        if not has_permission:
            raise ForbiddenException(
                key="permission",
                message=f"Permission denied. Required: {permission.name}"
            )
        return user_id
    return dependency
```

---

## Validation Errors

Pydantic validation errors are automatically converted to the standard error format.

### Request Schema

```python
from pydantic import BaseModel, EmailStr, field_validator

class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    confirm_password: str

    @field_validator("confirm_password")
    @classmethod
    def passwords_match(cls, v, info):
        if v != info.data.get("password"):
            raise ValueError("Passwords do not match")
        return v
```

### Validation Error Response

```json
{
  "error": {
    "logId": "abc123",
    "statusCode": 400,
    "type": "BadRequestException",
    "messages": {
      "email": "value is not a valid email address",
      "confirm_password": "Passwords do not match"
    }
  }
}
```

### How It Works

The validation middleware in `app/core/middlewares/validation_exception_middleware.py`:

1. Catches `RequestValidationError` from FastAPI
2. Extracts field names and error messages
3. Removes `body.` prefix from field paths
4. Returns consistent `ErrorResponse` format

---

## Middleware Configuration

### Registration Order

In `app/main.py`:

```python
from app.core.middlewares.exception_middleware import CustomExceptionMiddleware
from app.core.middlewares.validation_exception_middleware import custom_validation_exception_middleware

# Add exception middleware
app.add_middleware(CustomExceptionMiddleware)

# Add validation exception handler
app.exception_handler(RequestValidationError)(custom_validation_exception_middleware)
```

### Exception Middleware Flow

```
Request
   │
   ▼
┌─────────────────────────────┐
│  CustomExceptionMiddleware  │
│  - Catches custom exceptions│
│  - Catches unhandled errors │
│  - Logs with correlation ID │
│  - Returns ErrorResponse    │
└─────────────────────────────┘
   │
   ▼
┌─────────────────────────────┐
│     Route Handler           │
│  - May raise exceptions     │
└─────────────────────────────┘
   │
   ▼
Response (success or error)
```

### Handled Exception Types

| Exception | Status | When to Use |
|-----------|--------|-------------|
| `BadRequestException` | 400 | Invalid input, business rule violation |
| `UnauthorizedException` | 401 | Authentication required/failed |
| `ForbiddenException` | 403 | Not authorized for action |
| `NotFoundException` | 404 | Resource doesn't exist |
| `ConflictException` | 409 | Duplicate resource, version conflict |
| Unhandled `Exception` | 500 | Unexpected server error |

---

## Logging

All exceptions are logged with structured properties for Seq:

| Property | Description |
|----------|-------------|
| `LogId` | Correlation ID (same as response) |
| `UserId` | Authenticated user ID (if available) |
| `Type` | Exception type name |
| `StatusCode` | HTTP status code |
| `Path` | Request path |
| `HttpMethod` | GET, POST, etc. |
| `Error` | Error messages JSON |
| `StackTrace` | Stack trace (500 errors only) |

### Seq Queries

```
Type == "NotFoundException"
StatusCode >= 500
LogId == "abc-123"
Path == "/api/v1/users"
```

---

## Best Practices

1. **Use specific exceptions** — Choose the right exception type for the situation
2. **Provide clear messages** — Help API consumers understand the error
3. **Use meaningful keys** — Field names for validation, resource names for not found
4. **Don't catch and re-raise** — Let middleware handle responses
5. **Log additional context** — Use structured properties for debugging
6. **Keep services clean** — Throw exceptions, don't return error objects

### Example: Clean Service Method

```python
async def update_user(self, user_id: UUID, data: UpdateUserRequest) -> User:
    user = await self._user_repository.get_by_id(user_id)
    if not user:
        raise NotFoundException(key="user", message=f"User not found: {user_id}")
    
    if data.email != user.email:
        existing = await self._user_repository.get_by_email(data.email)
        if existing:
            raise ConflictException(key="email", message="Email already in use")
    
    user.email = data.email
    user.full_name = data.full_name
    return await self._user_repository.update(user)
```
