# Role-Based Access Control (RBAC) System

This document describes the production-grade RBAC system implementation for the FastAPI boilerplate.

## Overview

The RBAC system provides fine-grained permission-based authorization with:
- **Role-based permissions**: Users inherit permissions from their assigned roles (via UserRole → Role → RoleClaim)
- **Caching**: In-memory permission caching for high performance
- **Clean architecture**: Separation of concerns with repository, service, and dependency layers
- **System roles**: Pre-defined roles (Super Admin, Admin) with automatic permission seeding

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
│  - require_permission(AppPermissions.USERS_VIEW)                │
│  - require_any_permission(AppPermissions.A, AppPermissions.B)   │
│  - require_all_permissions(AppPermissions.A, AppPermissions.B)  │
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
│   ├── rbac/                                    # RBAC module folder
│   │   ├── __init__.py                          # Exports all RBAC components
│   │   ├── actions.py                           # AppAction enum (VIEW, SEARCH, CREATE, etc.)
│   │   ├── resources.py                         # AppResource enum (USERS, ROLES, DOCUMENTS, etc.)
│   │   ├── claims.py                            # AppClaim, PermissionClaimType
│   │   ├── permission_definition.py             # PermissionDefinition dataclass
│   │   ├── app_permissions.py                   # AppPermissions registry
│   │   ├── app_roles.py                         # AppRoles registry (SUPER_ADMIN, ADMIN)
│   │   ├── groups.py                            # PermissionGroups (USER_MANAGEMENT, etc.)
│   │   └── dependencies.py                      # FastAPI permission dependencies
│   └── seeders/
│       └── application.py                       # Seeds system roles with permissions
├── repositories/
│   ├── permission_repository.py                 # Permission data access
│   └── interfaces/
│       └── permission_repository_interface.py
├── services/
│   ├── permission_service.py                    # Permission checking with cache
│   └── interfaces/
│       └── permission_service_interface.py
└── schema/
    └── response/
        └── permission.py                        # PermissionResponse, PermissionClaimResponse
```

## Core Components

### AppAction - Available Actions

```python
from app.core.rbac import AppAction

class AppAction(str, Enum):
    VIEW = "view"
    SEARCH = "search"
    CREATE = "create"
    UPDATE = "update"
    UPSERT = "upsert"
    DELETE = "delete"
    EXECUTE = "execute"
    GENERATE = "generate"
    CLEAN = "clean"
    EXPORT = "export"
    IMPORT = "import"
    UPLOAD = "upload"
```

### AppResource - Available Resources

```python
from app.core.rbac import AppResource

class AppResource(str, Enum):
    USERS = "users"
    ROLES = "roles"
    ROLES_PERMISSIONS = "roles_permissions"
    DOCUMENTS = "documents"
```

### PermissionDefinition - Permission Record

```python
from app.core.rbac import PermissionDefinition

@dataclass(frozen=True)
class PermissionDefinition:
    description: str          # Brief description
    display_name: str         # Human-readable name for UI
    action: AppAction         # The action (VIEW, CREATE, etc.)
    resource: AppResource     # The resource (USERS, ROLES, etc.)
    is_show: bool = True      # Whether to show in UI
    
    @property
    def name(self) -> str:
        # Returns: "permission.{resource}.{action}"
        # Example: "permission.users.view"
```

### AppPermissions - Permission Registry

```python
from app.core.rbac import AppPermissions

# Access individual permissions
AppPermissions.USERS_VIEW      # PermissionDefinition for viewing users
AppPermissions.ROLES_CREATE    # PermissionDefinition for creating roles

# Get permission sets for roles
AppPermissions.super_admin()   # All permissions
AppPermissions.admin()         # Admin-level permissions
AppPermissions.all()           # List of all permissions
AppPermissions.visible()       # List of permissions where is_show=True
```

### AppRoles - System Roles Registry

```python
from app.core.rbac import AppRoles

# Role name constants
AppRoles.SUPER_ADMIN  # "SUPER_ADMIN"
AppRoles.ADMIN        # "ADMIN"

# Get all system roles
AppRoles.all()  # List[ApplicationSystemRole]
```

## Usage Examples

### 1. Single Permission (Most Common)

```python
from app.core.rbac import AppPermissions, require_permission

@router.get(
    "/users/{user_id}",
    dependencies=[Depends(require_permission(AppPermissions.USERS_VIEW))]
)
async def get_user(user_id: UUID):
    return {"user": {}}
```

### 2. Search/List Endpoints

```python
from app.core.rbac import AppPermissions, require_permission

@router.get(
    "/users/search",
    dependencies=[Depends(require_permission(AppPermissions.USERS_SEARCH))]
)
async def search_users():
    return {"users": []}
```

### 3. Multiple Permissions (OR Logic)

User needs **any one** of the listed permissions:

```python
from app.core.rbac import AppPermissions, require_any_permission

@router.get(
    "/dashboard",
    dependencies=[Depends(require_any_permission(
        AppPermissions.ROLES_VIEW,
        AppPermissions.USERS_VIEW
    ))]
)
async def view_dashboard():
    return {"dashboard": "data"}
```

### 4. Multiple Permissions (AND Logic)

User needs **all** listed permissions:

```python
from app.core.rbac import AppPermissions, require_all_permissions

@router.delete(
    "/system/purge",
    dependencies=[Depends(require_all_permissions(
        AppPermissions.USERS_DELETE,
        AppPermissions.ROLES_DELETE
    ))]
)
async def purge_system():
    return {"status": "purged"}
```

### 5. Dynamic Permission Checking

Check permissions within the route handler:

```python
from app.core.rbac import AppPermissions, get_current_user_with_permissions, CurrentUserWithPermissions

@router.get("/items/{item_id}")
async def get_item(
    item_id: int,
    current_user: CurrentUserWithPermissions = Depends(get_current_user_with_permissions)
):
    item = await get_item_by_id(item_id)
    
    # Add permission-based flags
    item.can_edit = current_user.has_permission(AppPermissions.DOCUMENTS_UPDATE)
    item.can_delete = current_user.has_permission(AppPermissions.DOCUMENTS_DELETE)
    
    return item
```

### 6. Router-Level Protection

Protect all endpoints in a router:

```python
from app.core.rbac import AppPermissions, require_permission

admin_router = APIRouter(
    prefix="/admin",
    dependencies=[
        Depends(JWTBearer()),
        Depends(require_permission(AppPermissions.ROLES_VIEW))
    ]
)

@admin_router.get("/stats")
async def get_stats():
    # Only users with ROLES_VIEW can access
    return {"stats": "..."}
```

### 7. Get User ID from Permission Dependency

The permission dependency returns the user_id:

```python
from app.core.rbac import AppPermissions, require_permission

@router.get("/my-data")
async def get_my_data(
    user_id: UUID = Depends(require_permission(AppPermissions.USERS_VIEW))
):
    # user_id is available after permission check passes
    return {"user_id": str(user_id)}
```

## Permission Definitions

Permissions are defined in `app/core/rbac/app_permissions.py`:

```python
class AppPermissions:
    # User Management
    USERS_SEARCH = PermissionDefinition(
        description="Search users",
        display_name="Users",
        action=AppAction.SEARCH,
        resource=AppResource.USERS,
    )
    USERS_VIEW = PermissionDefinition(
        description="View user details",
        display_name="Users",
        action=AppAction.VIEW,
        resource=AppResource.USERS,
    )
    USERS_CREATE = PermissionDefinition(...)
    USERS_UPDATE = PermissionDefinition(...)
    USERS_DELETE = PermissionDefinition(...)
    
    # Role Management
    ROLES_SEARCH = PermissionDefinition(...)
    ROLES_VIEW = PermissionDefinition(...)
    ROLES_CREATE = PermissionDefinition(...)
    ROLES_UPDATE = PermissionDefinition(...)
    ROLES_DELETE = PermissionDefinition(...)
    
    # Document Management
    DOCUMENTS_VIEW = PermissionDefinition(...)
    DOCUMENTS_UPLOAD = PermissionDefinition(...)
    DOCUMENTS_UPDATE = PermissionDefinition(...)
    DOCUMENTS_DELETE = PermissionDefinition(...)
```

### Permission Naming Convention

Permission names follow the format: `permission.{resource}.{action}`

| Action | Permission Name | Usage |
|--------|-----------------|-------|
| `SEARCH` | `permission.users.search` | List/search endpoints |
| `VIEW` | `permission.users.view` | Get single item by ID |
| `CREATE` | `permission.users.create` | Create new items |
| `UPDATE` | `permission.users.update` | Update existing items |
| `DELETE` | `permission.users.delete` | Delete items |

### Adding New Permissions

1. Add the resource to `AppResource` enum in `app/core/rbac/resources.py` (if new)
2. Add the action to `AppAction` enum in `app/core/rbac/actions.py` (if new)
3. Add the permission to `AppPermissions` class in `app/core/rbac/app_permissions.py`
4. Add to the `all()` method list
5. Assign to role permission sets (`super_admin()`, `admin()`) as needed

```python
# 1. Add resource (if new)
class AppResource(str, Enum):
    REPORTS = "reports"

# 2. Add permission in AppPermissions
REPORTS_VIEW = PermissionDefinition(
    description="View reports",
    display_name="Reports",
    action=AppAction.VIEW,
    resource=AppResource.REPORTS
)

# 3. Add to all() list
@classmethod
def all(cls) -> list[PermissionDefinition]:
    return [
        # ... existing permissions
        cls.REPORTS_VIEW,
    ]

# 4. Add to role permission sets
@classmethod
def admin(cls) -> list[PermissionDefinition]:
    return [
        # ... existing permissions
        cls.REPORTS_VIEW,
    ]
```

## System Roles and Seeding

### AppRoles - System Role Definitions

```python
from app.core.rbac import AppRoles, ApplicationSystemRole

class AppRoles:
    SUPER_ADMIN = "SUPER_ADMIN"
    ADMIN = "ADMIN"
    
    _system_roles = [
        ApplicationSystemRole(
            name="Super Admin",
            normalized_name=SUPER_ADMIN,
            description="Role with all permissions",
            is_editable=False
        ),
        ApplicationSystemRole(
            name="Admin",
            normalized_name=ADMIN,
            description="Administrator role with management permissions",
            is_editable=False
        ),
    ]
```

### Seeding System Roles

The `ApplicationSeeder` in `app/core/seeders/application.py`:

```python
async def seed_system_roles(self, session: AsyncSession):
    for system_role in AppRoles.all():
        # Create or update role
        role = Role(
            name=system_role.name,
            normalized_name=system_role.normalized_name,
            description=system_role.description,
            is_system=not system_role.is_editable
        )
        
        # Assign permissions based on role
        if system_role.normalized_name == AppRoles.SUPER_ADMIN:
            await self.assign_permissions_to_role(
                session, role, AppPermissions.super_admin()
            )
        elif system_role.normalized_name == AppRoles.ADMIN:
            await self.assign_permissions_to_role(
                session, role, AppPermissions.admin()
            )
```

### Permission Sync (Add/Remove)

The seeder automatically syncs permissions:
- **Adds** new permissions not in database
- **Removes** permissions no longer in the permission set

```python
async def assign_permissions_to_role(self, session, role, permissions):
    existing_claims = {claim.claim_name: claim for claim in existing}
    target_permissions = {perm.name for perm in permissions}
    
    # Add new
    for perm in permissions:
        if perm.name not in existing_claims:
            session.add(RoleClaim(...))
    
    # Remove old
    for perm_name in existing_claims:
        if perm_name not in target_permissions:
            await session.delete(existing_claims[perm_name])
```

## Database Schema

### role_claims Table

```sql
CREATE TABLE identity.role_claims (
    id UUID PRIMARY KEY,
    claim_type VARCHAR(256) NOT NULL,  -- 'permission'
    claim_name VARCHAR(256) NOT NULL,  -- 'permission.users.view'
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

## API Endpoints

### Get All Permissions

`GET /roles/permissions` - Returns all visible permissions grouped by resource:

```json
[
  {
    "name": "Roles",
    "claims": [
      {
        "action": "Search",
        "description": "Search roles",
        "permission": "Permission.Roles.Search"
      },
      {
        "action": "View",
        "description": "View role details",
        "permission": "Permission.Roles.View"
      },
      {
        "action": "Create",
        "description": "Create new roles",
        "permission": "Permission.Roles.Create"
      }
    ]
  },
  {
    "name": "Documents",
    "claims": [...]
  }
]
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

## Error Responses

When permission check fails:

```json
{
    "detail": "Permission denied. Required: permission.users.view"
}
```

For multiple permissions (OR):
```json
{
    "detail": "Permission denied. Required any of: permission.roles.view, permission.users.view"
}
```

For multiple permissions (AND):
```json
{
    "detail": "Permission denied. Required all of: permission.users.delete, permission.roles.delete"
}
```

## Real-World Example: Role Endpoints

See `app/api/endpoints/v1/role.py` for a complete implementation:

```python
from app.core.rbac import AppPermissions, require_permission

# Search - requires roles.search
@router.get("/search", dependencies=[Depends(require_permission(AppPermissions.ROLES_SEARCH))])

# View - requires roles.view  
@router.get("/{role_id}", dependencies=[Depends(require_permission(AppPermissions.ROLES_VIEW))])

# Create - requires roles.create
@router.post("/", dependencies=[Depends(require_permission(AppPermissions.ROLES_CREATE))])

# Update - requires roles.update
@router.put("/{role_id}", dependencies=[Depends(require_permission(AppPermissions.ROLES_UPDATE))])

# Delete - requires roles.delete
@router.delete("/{role_id}", dependencies=[Depends(require_permission(AppPermissions.ROLES_DELETE))])
```

## Testing

Example test for protected endpoint:

```python
async def test_roles_search_requires_permission():
    # User without permission
    response = await client.get("/roles/search", headers=auth_headers)
    assert response.status_code == 403
    
    # Add permission to user's role
    await add_permission_to_role(role_id, "permission.roles.search")
    
    # Clear cache
    await permission_service.invalidate_user_permissions_cache(user_id)
    
    # Now should succeed
    response = await client.get("/roles/search", headers=auth_headers)
    assert response.status_code == 200
```
