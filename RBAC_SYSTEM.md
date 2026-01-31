# Role-Based Access Control (RBAC) System

This document describes the production-grade RBAC system implementation for the FastAPI boilerplate.

## Overview

The RBAC system provides fine-grained permission-based authorization with:
- **Role-based permissions**: Users inherit permissions from their assigned roles (via UserRole → Role → RoleClaim)
- **Caching**: In-memory permission caching for high performance
- **Clean architecture**: Separation of concerns with repository, service, and dependency layers

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        FastAPI Routes                            │
│  (Use require_permission, require_any_permission, etc.)         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                 app/core/rbac/dependencies.py                    │
│  - require_permission(Permission.USERS_VIEW)                    │
│  - require_any_permission(Permission.A, Permission.B)           │
│  - require_all_permissions(Permission.A, Permission.B)          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    PermissionService                             │
│  - Caches permissions per user (5 min TTL)                      │
│  - Checks single/multiple permissions                            │
│  - Invalidates cache on permission changes                       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   PermissionRepository                           │
│  - Loads permissions from database                               │
│  - Queries: user_roles → role_claims                             │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Database Tables                             │
│  - users, roles, user_roles, role_claims                         │
└─────────────────────────────────────────────────────────────────┘
```

## File Structure

```
app/
├── core/
│   └── rbac/                            # RBAC module folder
│       ├── __init__.py                  # Exports all RBAC components
│       ├── permissions.py               # Permission enum definitions
│       └── dependencies.py              # FastAPI permission dependencies
├── repositories/
│   ├── permission_repository.py         # Permission data access
│   └── interfaces/
│       └── permission_repository_interface.py
└── services/
    ├── permission_service.py            # Permission checking with cache
    └── interfaces/
        └── permission_service_interface.py
```

## Usage Examples

### 1. Single Permission (Most Common)

```python
from app.core.rbac import Permission, require_permission

@router.get(
    "/users",
    dependencies=[Depends(require_permission(Permission.USERS_VIEW))]
)
async def get_user():
    return {"user": {}}
```

### 2. Search/List Endpoints

```python
from app.core.rbac import Permission, require_permission

@router.get(
    "/users/search",
    dependencies=[Depends(require_permission(Permission.USERS_SEARCH))]
)
async def search_users():
    return {"users": []}
```

### 3. Multiple Permissions (OR Logic)

User needs **any one** of the listed permissions:

```python
from app.core.rbac import Permission, require_any_permission

@router.get(
    "/dashboard",
    dependencies=[Depends(require_any_permission(
        Permission.ADMIN_ACCESS,
        Permission.AUDIT_VIEW
    ))]
)
async def view_dashboard():
    return {"dashboard": "data"}
```

### 4. Multiple Permissions (AND Logic)

User needs **all** listed permissions:

```python
from app.core.rbac import Permission, require_all_permissions

@router.delete(
    "/system/purge",
    dependencies=[Depends(require_all_permissions(
        Permission.ADMIN_ACCESS,
        Permission.SYSTEM_SETTINGS
    ))]
)
async def purge_system():
    return {"status": "purged"}
```

### 5. Dynamic Permission Checking

Check permissions within the route handler:

```python
from app.core.rbac import Permission, get_current_user_with_permissions, CurrentUserWithPermissions

@router.get("/items/{item_id}")
async def get_item(
    item_id: int,
    current_user: CurrentUserWithPermissions = Depends(get_current_user_with_permissions)
):
    item = await get_item_by_id(item_id)
    
    # Add permission-based flags
    item.can_edit = current_user.has_permission(Permission.DOCUMENTS_UPDATE)
    item.can_delete = current_user.has_permission(Permission.DOCUMENTS_DELETE)
    
    return item
```

### 6. Router-Level Protection

Protect all endpoints in a router:

```python
from app.core.rbac import Permission, require_permission

admin_router = APIRouter(
    prefix="/admin",
    dependencies=[
        Depends(JWTBearer()),
        Depends(require_permission(Permission.ADMIN_ACCESS))
    ]
)

@admin_router.get("/stats")
async def get_stats():
    # Only admins can access
    return {"stats": "..."}
```

### 7. Get User ID from Permission Dependency

The permission dependency returns the user_id:

```python
from app.core.rbac import Permission, require_permission

@router.get("/my-data")
async def get_my_data(
    user_id: UUID = Depends(require_permission(Permission.USERS_VIEW))
):
    # user_id is available after permission check passes
    return {"user_id": str(user_id)}
```

## Permission Definitions

Permissions are defined as an Enum in `app/core/rbac/permissions.py`:

```python
class Permission(str, Enum):
    # User Management
    USERS_SEARCH = "users.search"       # Search/list users
    USERS_VIEW = "users.view"           # View single user details
    USERS_CREATE = "users.create"       # Create new users
    USERS_UPDATE = "users.update"       # Update existing users
    USERS_DELETE = "users.delete"       # Delete users
    
    # Role Management
    ROLES_SEARCH = "roles.search"       # Search/list roles
    ROLES_VIEW = "roles.view"           # View single role details
    ROLES_CREATE = "roles.create"       # Create new roles
    ROLES_UPDATE = "roles.update"       # Update role details
    ROLES_DELETE = "roles.delete"       # Delete roles
    
    # Document Management
    DOCUMENTS_SEARCH = "documents.search"
    DOCUMENTS_VIEW = "documents.view"
    DOCUMENTS_UPLOAD = "documents.upload"
    DOCUMENTS_UPDATE = "documents.update"
    DOCUMENTS_DELETE = "documents.delete"
    
    # System/Admin
    ADMIN_ACCESS = "admin.access"
    SYSTEM_SETTINGS = "system.settings"
    AUDIT_VIEW = "audit.view"
```

### Permission Naming Convention

| Action | Permission | Usage |
|--------|------------|-------|
| `SEARCH` | `{resource}.search` | List/search endpoints |
| `VIEW` | `{resource}.view` | Get single item by ID |
| `CREATE` | `{resource}.create` | Create new items |
| `UPDATE` | `{resource}.update` | Update existing items |
| `DELETE` | `{resource}.delete` | Delete items |

### Adding New Permissions

1. Add to the `Permission` enum in `app/core/rbac/permissions.py`
2. Assign to roles via `role_claims` table

## Database Schema

### role_claims Table
```sql
CREATE TABLE identity.role_claims (
    id UUID PRIMARY KEY,
    claim_type VARCHAR(256) NOT NULL,  -- 'permission'
    claim_name VARCHAR(256) NOT NULL,  -- 'users.view'
    role_id UUID NOT NULL REFERENCES identity.roles(id),
    created_at TIMESTAMP,
    created_by VARCHAR(256),
    updated_at TIMESTAMP,
    updated_by VARCHAR(256)
);
```

### Permission Flow
```
User → UserRole → Role → RoleClaim (where claim_type = 'permission')
```

## Performance Optimizations

### 1. Permission Caching

Permissions are cached per user with a 5-minute sliding expiration:

```python
class PermissionService:
    CACHE_KEY_PREFIX = "permissions"
    CACHE_TTL_SECONDS = 300  # 5 minutes
```

### 2. Cache Invalidation

Call these methods when permissions change:

```python
# When user roles change
await permission_service.invalidate_user_permissions_cache(user_id)

# When role permissions change (invalidates all users with that role)
await permission_service.invalidate_role_permissions_cache(role_id)
```

### 3. Batch Permission Loading

All permissions are loaded at once (not per-permission), reducing database queries.

## Configuration

The RBAC system uses the cache service configured in `container.py`:

```python
permission_service = providers.Factory(
    PermissionService,
    permission_repository=permission_repository,
    cache_service=cache_service  # Can be None, InMemory, or Redis
)
```

## Error Responses

When permission check fails:

```json
{
    "detail": "Permission denied. Required: users.view"
}
```

For multiple permissions (OR):
```json
{
    "detail": "Permission denied. Required any of: admin.access, audit.view"
}
```

For multiple permissions (AND):
```json
{
    "detail": "Permission denied. Required all of: admin.access, system.settings"
}
```

## Real-World Example: Role Endpoints

See `app/api/endpoints/v1/role.py` for a complete implementation:

```python
from app.core.rbac import Permission, require_permission

# Search - requires roles.search
@router.get("/search", dependencies=[Depends(require_permission(Permission.ROLES_SEARCH))])

# View - requires roles.view  
@router.get("/{role_id}", dependencies=[Depends(require_permission(Permission.ROLES_VIEW))])

# Create - requires roles.create
@router.post("/", dependencies=[Depends(require_permission(Permission.ROLES_CREATE))])

# Update - requires roles.update
@router.put("/{role_id}", dependencies=[Depends(require_permission(Permission.ROLES_UPDATE))])

# Delete - requires roles.delete
@router.delete("/{role_id}", dependencies=[Depends(require_permission(Permission.ROLES_DELETE))])
```

## Testing

Example test for protected endpoint:

```python
async def test_roles_search_requires_permission():
    # User without permission
    response = await client.get("/roles/search", headers=auth_headers)
    assert response.status_code == 403
    
    # Add permission to user's role
    await add_permission_to_role(role_id, "roles.search")
    
    # Clear cache
    await permission_service.invalidate_user_permissions_cache(user_id)
    
    # Now should succeed
    response = await client.get("/roles/search", headers=auth_headers)
    assert response.status_code == 200
```
