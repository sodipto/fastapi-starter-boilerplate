# REST API Conventions

Guidelines for designing consistent, predictable, and maintainable REST APIs.

## Table of Contents

- [URL Structure](#url-structure)
- [HTTP Methods](#http-methods)
- [Status Codes](#status-codes)
- [Naming Conventions](#naming-conventions)
- [Path Parameters](#path-parameters)
- [Query Parameters](#query-parameters)
- [Request/Response Bodies](#requestresponse-bodies)
- [Pagination](#pagination)
- [Versioning](#versioning)
- [Examples](#examples)

---

## URL Structure

### Base Pattern

```
/api/{version}/{resource}/{id}/{sub-resource}
```

### Rules

| Rule | ✅ Correct | ❌ Incorrect |
|------|-----------|-------------|
| Use lowercase | `/api/v1/users` | `/api/v1/Users` |
| Use plural nouns | `/api/v1/users` | `/api/v1/user` |
| Use hyphens for multi-word | `/api/v1/user-roles` | `/api/v1/userRoles` |
| No trailing slashes | `/api/v1/users` | `/api/v1/users/` |
| No file extensions | `/api/v1/users` | `/api/v1/users.json` |
| No verbs in paths | `/api/v1/users` | `/api/v1/getUsers` |

---

## HTTP Methods

| Method | Purpose | Idempotent | Request Body | Example |
|--------|---------|------------|--------------|---------|
| `GET` | Retrieve resource(s) | Yes | No | `GET /users/123` |
| `POST` | Create new resource | No | Yes | `POST /users` |
| `PUT` | Replace entire resource | Yes | Yes | `PUT /users/123` |
| `PATCH` | Partial update | Yes | Yes | `PATCH /users/123/status` |
| `DELETE` | Remove resource | Yes | No | `DELETE /users/123` |

### Method Selection Guide

```
Need to retrieve data?                    → GET
Need to create a new resource?            → POST
Need to replace entire resource?          → PUT
Need to update specific fields?           → PATCH
Need to remove a resource?                → DELETE
Need to perform an action (not CRUD)?     → POST with action endpoint
```

---

## Status Codes

### Success Codes

| Code | Name | When to Use |
|------|------|-------------|
| `200` | OK | Successful GET, PUT, PATCH |
| `201` | Created | Successful POST (resource created) |
| `204` | No Content | Successful DELETE (no body returned) |

### Client Error Codes

| Code | Name | When to Use |
|------|------|-------------|
| `400` | Bad Request | Invalid input, validation failed |
| `401` | Unauthorized | Missing or invalid authentication |
| `403` | Forbidden | Authenticated but not authorized |
| `404` | Not Found | Resource doesn't exist |
| `409` | Conflict | Duplicate resource, version conflict |
| `422` | Unprocessable Entity | Semantic validation error |

### Server Error Codes

| Code | Name | When to Use |
|------|------|-------------|
| `500` | Internal Server Error | Unexpected server error |
| `503` | Service Unavailable | Server temporarily unavailable |

---

## Naming Conventions

### Resources

| Resource Type | Naming | Example |
|---------------|--------|---------|
| Collection | Plural noun | `/users`, `/roles`, `/orders` |
| Singleton | Singular noun | `/users/123/profile` |
| Sub-resource | Nested under parent | `/users/123/roles` |

### Actions (Non-CRUD Operations)

For operations that don't fit CRUD, use action endpoints:

```
POST /auth/login              # Authentication action
POST /auth/logout             # Logout action
POST /auth/refresh-token      # Token refresh action
POST /auth/forgot-password    # Password reset request
POST /auth/reset-password     # Password reset execution
POST /users/123/activate      # Activate user
POST /orders/456/cancel       # Cancel order
```

### Common Patterns

| Pattern | URL | Method | Purpose |
|---------|-----|--------|---------|
| List | `/users` | GET | Get all users |
| Create | `/users` | POST | Create user |
| Read | `/users/{id}` | GET | Get single user |
| Update | `/users/{id}` | PUT | Replace user |
| Partial Update | `/users/{id}/status` | PATCH | Update status |
| Delete | `/users/{id}` | DELETE | Delete user |
| Sub-resource | `/users/{id}/roles` | GET | Get user's roles |
| Search | `/users` | GET | Search with query params |
| Action | `/users/{id}/activate` | POST | Perform action |

---

## Path Parameters

### When to Use

Path parameters identify specific resources:

```python
# Good: ID in path identifies resource
GET  /users/{id}
PUT  /users/{id}

# Good: Nested resource
GET  /users/{user_id}/roles
GET  /users/{user_id}/roles/{role_id}
```

### FastAPI Implementation

```python
from uuid import UUID

@router.get("/{id}")
async def get_by_id(id: UUID):
    """Get user by ID."""
    return await user_service.get_by_id(id)

@router.get("/{user_id}/roles")
async def get_user_roles(user_id: UUID):
    """Get all roles for a user."""
    return await user_service.get_user_roles(user_id)
```

### Parameter Naming

| ✅ Good | ❌ Bad | Reason |
|---------|--------|--------|
| `{id}` | `{userId}` | Use `id` for primary resource |
| `{user_id}` | `{userId}` | Use snake_case in Python |
| `{role_id}` | `{roleID}` | Consistent casing |

---

## Query Parameters

### When to Use

Query parameters for filtering, sorting, pagination, and optional data:

```
GET /users?email=john@example.com        # Filter by email
GET /users?is_active=true                # Filter by status
GET /users?page=1&page_size=20           # Pagination
GET /users?sort_by=created_at&order=desc # Sorting
GET /users?include=roles,profile         # Include related data
```

### FastAPI Implementation

```python
@router.get("")
async def search(
    email: str | None = None,           # Optional filter
    full_name: str | None = None,       # Optional filter
    is_active: bool | None = None,      # Optional filter
    page: int = 1,                      # Pagination with default
    page_size: int = 20,                # Pagination with default
):
    """Search users with filters and pagination."""
    return await user_service.search(
        page=page,
        page_size=page_size,
        email=email,
        full_name=full_name,
        is_active=is_active
    )
```

### Common Query Parameters

| Parameter | Purpose | Example |
|-----------|---------|---------|
| `page` | Page number | `?page=2` |
| `page_size` | Items per page | `?page_size=50` |
| `sort_by` | Sort field | `?sort_by=created_at` |
| `order` | Sort direction | `?order=desc` |
| `search` | Full-text search | `?search=john` |
| `include` | Related resources | `?include=roles` |
| `fields` | Sparse fieldsets | `?fields=id,email` |

---

## Request/Response Bodies

### Request Body Rules

1. Use for `POST`, `PUT`, `PATCH` methods
2. Use camelCase for JSON keys (API consumers)
3. Define clear Pydantic schemas

```python
# app/schema/request/identity/user.py
from pydantic import BaseModel, EmailStr

class UserRequest(BaseModel):
    email: EmailStr
    full_name: str
    phone_number: str | None = None
    is_active: bool = True

    class Config:
        # Convert snake_case to camelCase in JSON
        populate_by_name = True
```

### Response Body Rules

1. Always return consistent structure
2. Include metadata for lists (pagination)
3. Use proper status codes

```python
# Single resource
{
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "john@example.com",
    "fullName": "John Doe",
    "createdAt": "2024-01-15T10:30:00Z"
}

# Collection with pagination
{
    "items": [...],
    "meta": {
        "page": 1,
        "pageSize": 20,
        "totalItems": 150,
        "totalPages": 8
    }
}

# Error response
{
    "error": {
        "logId": "abc-123",
        "statusCode": 400,
        "type": "BadRequestException",
        "messages": {
            "email": "Invalid email format"
        }
    }
}
```

---

## Pagination

### Request

```
GET /users?page=1&page_size=20
```

### Response Structure

```json
{
    "items": [
        {"id": "1", "email": "user1@example.com"},
        {"id": "2", "email": "user2@example.com"}
    ],
    "meta": {
        "page": 1,
        "pageSize": 20,
        "totalItems": 150,
        "totalPages": 8
    }
}
```

### FastAPI Schema

```python
from pydantic import BaseModel
from typing import Generic, TypeVar

T = TypeVar("T")

class PaginationMeta(BaseModel):
    page: int
    page_size: int
    total_items: int
    total_pages: int

class PagedData(BaseModel, Generic[T]):
    items: list[T]
    meta: PaginationMeta
```

---

## Versioning

### URL Versioning (Recommended)

```
/api/v1/users
/api/v2/users
```

### Implementation

```python
# app/api/endpoints/routes.py
from fastapi import APIRouter

routers = APIRouter()
routers.include_router(auth_router)
routers.include_router(user_router)
routers.include_router(role_router)

# app/main.py
app.include_router(routers, prefix="/api/v1")
```

---

## Examples

### Authentication Endpoints

```python
router = APIRouter(prefix="/auth", tags=["Authentication"])

# POST /api/v1/auth/signup
@router.post("/signup", response_model=ResponseMeta)
async def signup(payload: SignupRequest): ...

# POST /api/v1/auth/login
@router.post("/login", response_model=AuthResponse)
async def login(payload: LoginRequest): ...

# POST /api/v1/auth/refresh-token
@router.post("/refresh-token", response_model=AuthResponse)
async def refresh_token(payload: TokenRefreshRequest): ...

# POST /api/v1/auth/confirm-email
@router.post("/confirm-email", response_model=ResponseMeta)
async def confirm_email(payload: ConfirmEmailRequest): ...

# POST /api/v1/auth/forgot-password
@router.post("/forgot-password", response_model=ResponseMeta)
async def forgot_password(payload: ForgotPasswordRequest): ...

# POST /api/v1/auth/reset-password
@router.post("/reset-password", response_model=ResponseMeta)
async def reset_password(payload: ResetPasswordRequest): ...
```

### User CRUD Endpoints

```python
router = APIRouter(prefix="/users", tags=["Users"])

# GET /api/v1/users - Search/List users
@router.get("", response_model=PagedData[UserSearchResponse])
async def search(
    email: str | None = None,
    is_active: bool | None = None,
    page: int = 1,
    page_size: int = 20
): ...

# POST /api/v1/users - Create user
@router.post("", response_model=UserResponse, status_code=201)
async def create(user_request: UserRequest): ...

# GET /api/v1/users/{id} - Get user by ID
@router.get("/{id}", response_model=UserResponse)
async def get_by_id(id: UUID): ...

# PUT /api/v1/users/{id} - Update user
@router.put("/{id}", response_model=UserResponse)
async def update(id: UUID, user_request: UserUpdateRequest): ...

# PATCH /api/v1/users/{id}/status - Update user status
@router.patch("/{id}/status", response_model=UserResponse)
async def update_status(id: UUID, status_request: UserStatusRequest): ...

# DELETE /api/v1/users/{id} - Delete user
@router.delete("/{id}", status_code=204)
async def delete(id: UUID): ...

# GET /api/v1/users/{id}/roles - Get user roles (sub-resource)
@router.get("/{id}/roles", response_model=list[UserRoleResponse])
async def get_user_roles(id: UUID): ...
```

### Role CRUD Endpoints

```python
router = APIRouter(prefix="/roles", tags=["Roles"])

# GET /api/v1/roles/permissions - Get all permissions
@router.get("/permissions", response_model=list[PermissionResponse])
async def get_all_permissions(): ...

# GET /api/v1/roles/search - Search roles
@router.get("/search", response_model=PagedData[RoleSearchResponse])
async def search(name: str | None = None, page: int = 1): ...

# POST /api/v1/roles - Create role
@router.post("/", response_model=RoleResponse, status_code=201)
async def create(role_request: RoleRequest): ...

# GET /api/v1/roles/{id} - Get role by ID
@router.get("/{id}", response_model=RoleResponse)
async def get(id: UUID): ...

# PUT /api/v1/roles/{id} - Update role
@router.put("/{id}", response_model=RoleResponse)
async def update(id: UUID, role_request: RoleRequest): ...

# DELETE /api/v1/roles/{id} - Delete role
@router.delete("/{id}", status_code=204)
async def delete(id: UUID): ...
```

---

## Quick Reference

### Endpoint Checklist

- [ ] Use plural nouns for resources
- [ ] Use lowercase with hyphens
- [ ] Use correct HTTP method
- [ ] Return appropriate status code
- [ ] Include `response_model` for type safety
- [ ] Add `summary` and docstring
- [ ] Apply authentication/authorization
- [ ] Handle errors consistently

### Common Mistakes

| ❌ Mistake | ✅ Correct |
|-----------|-----------|
| `GET /getUsers` | `GET /users` |
| `POST /users/create` | `POST /users` |
| `GET /user/1` | `GET /users/1` |
| `DELETE /users/1/delete` | `DELETE /users/1` |
| `PUT /updateUser/1` | `PUT /users/1` |
| Return 200 for create | Return 201 for create |
| Return body for delete | Return 204 (no body) |
