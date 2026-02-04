# Role-Based Access Control (RBAC)

Fine-grained permission system with caching and role inheritance.

## Table of Contents

- [Overview](#overview)
- [Protecting Endpoints](#protecting-endpoints)
- [Permission Definitions](#permission-definitions)
- [System Roles](#system-roles)
- [Adding Permissions](#adding-permissions)
- [Cache Management](#cache-management)

---

## Overview

Users inherit permissions through: `User → UserRole → Role → RoleClaim`

```
┌─────────────────────────────────────┐
│           FastAPI Routes            │
│  require_permission(AppPermissions) │
└─────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│         PermissionService           │
│   (5-min cache per user)            │
└─────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│        PermissionRepository         │
│   user_roles → role_claims          │
└─────────────────────────────────────┘
```

---

## Protecting Endpoints

### Single Permission

```python
from app.core.rbac import AppPermissions, require_permission

@router.get(
    "/users/{user_id}",
    dependencies=[Depends(require_permission(AppPermissions.USERS_VIEW))]
)
async def get_user(user_id: UUID):
    return {"user": {}}
```

### Any Permission (OR Logic)

User needs **one of** the listed permissions:

```python
from app.core.rbac import require_any_permission

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

### All Permissions (AND Logic)

User needs **all** listed permissions:

```python
from app.core.rbac import require_all_permissions

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

### Dynamic Permission Check

```python
from app.core.rbac import get_current_user_with_permissions, CurrentUserWithPermissions

@router.get("/items/{item_id}")
async def get_item(
    item_id: int,
    current_user: CurrentUserWithPermissions = Depends(get_current_user_with_permissions)
):
    item = await get_item_by_id(item_id)
    item.can_edit = current_user.has_permission(AppPermissions.DOCUMENTS_UPDATE)
    item.can_delete = current_user.has_permission(AppPermissions.DOCUMENTS_DELETE)
    return item
```

### Router-Level Protection

```python
admin_router = APIRouter(
    prefix="/admin",
    dependencies=[
        Depends(JWTBearer()),
        Depends(require_permission(AppPermissions.ROLES_VIEW))
    ]
)
```

---

## Permission Definitions

Permissions follow the format: `permission.{resource}.{action}`

### Available Actions

| Action | Usage |
|--------|-------|
| `SEARCH` | List/search endpoints |
| `VIEW` | Get single item |
| `CREATE` | Create new items |
| `UPDATE` | Update existing |
| `DELETE` | Delete items |
| `UPLOAD` | File uploads |
| `EXPORT` | Export data |

### Available Permissions

| Permission | Description |
|------------|-------------|
| `USERS_SEARCH` | Search users |
| `USERS_VIEW` | View user details |
| `USERS_CREATE` | Create users |
| `USERS_UPDATE` | Update users |
| `USERS_DELETE` | Delete users |
| `ROLES_SEARCH` | Search roles |
| `ROLES_VIEW` | View role details |
| `ROLES_CREATE` | Create roles |
| `ROLES_UPDATE` | Update roles |
| `ROLES_DELETE` | Delete roles |
| `DOCUMENTS_VIEW` | View documents |
| `DOCUMENTS_UPLOAD` | Upload documents |
| `DOCUMENTS_UPDATE` | Update documents |
| `DOCUMENTS_DELETE` | Delete documents |

---

## System Roles

Pre-defined roles seeded on application startup:

| Role | Permissions |
|------|-------------|
| `SUPER_ADMIN` | All permissions |
| `ADMIN` | Management permissions |
| `CUSTOMER` | Basic user permissions |

### Get Role Permissions

```python
from app.core.rbac import AppRoles, AppPermissions

# All permissions for super admin
permissions = AppPermissions.super_admin()

# Admin permissions
permissions = AppPermissions.admin()

# All defined permissions
permissions = AppPermissions.all()
```

---

## Adding Permissions

### 1. Add Resource (if new)

```python
# app/core/rbac/resources.py
class AppResource(str, Enum):
    REPORTS = "reports"
```

### 2. Define Permission

```python
# app/core/rbac/app_permissions.py
class AppPermissions:
    REPORTS_VIEW = PermissionDefinition(
        description="View reports",
        display_name="Reports",
        action=AppAction.VIEW,
        resource=AppResource.REPORTS
    )
```

### 3. Add to `all()` Method

```python
@classmethod
def all(cls) -> list[PermissionDefinition]:
    return [
        # ... existing
        cls.REPORTS_VIEW,
    ]
```

### 4. Assign to Roles

```python
@classmethod
def admin(cls) -> list[PermissionDefinition]:
    return [
        # ... existing
        cls.REPORTS_VIEW,
    ]
```

---

## Cache Management

Permissions are cached for 5 minutes per user.

### Invalidate User Cache

```python
await permission_service.invalidate_user_permissions_cache(user_id)
```

### Invalidate Role Cache

When role permissions change:

```python
await permission_service.invalidate_role_permissions_cache(role_id)
```

---

## Error Responses

```json
{
    "detail": "Permission denied. Required: permission.users.view"
}
```

For multiple permissions:

```json
{
    "detail": "Permission denied. Required any of: permission.roles.view, permission.users.view"
}
```

---

## API Endpoints

### Get All Permissions

`GET /roles/permissions` — Returns grouped permissions:

```json
[
  {
    "name": "Users",
    "claims": [
      {"action": "Search", "permission": "permission.users.search"},
      {"action": "View", "permission": "permission.users.view"}
    ]
  }
]
```
