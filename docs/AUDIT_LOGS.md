# Audit Logs

This document describes audit logging configuration and the public API for viewing audit logs.

## Configuration / Environment variables

- `AUDIT_ENABLED` (bool): Enable or disable audit logging. Default: `True` in example env files.
- `AUDIT_SENSITIVE_FIELDS` (comma-separated string or list): Fields to exclude or mask from audit payloads (e.g. `password`, `tokens`).

Examples (`.env`):

```
AUDIT_ENABLED=True
AUDIT_SENSITIVE_FIELDS=password,refresh_token,tokens
```

### How settings are loaded

The project uses `pydantic-settings` via `app.core.config.Settings`. `AUDIT_SENSITIVE_FIELDS` accepts either a comma-separated string or a JSON/list and is normalized to a `list[str]` by a validator so other code can treat it uniformly.

Use `settings.AUDIT_SENSITIVE_FIELDS` in audit logic to redact sensitive values before they are persisted to the `audit_logs` table.

## API Endpoints

All audit endpoints require authentication and the `permission.audit_logs.search` permission. The app enforces this with the RBAC dependency `require_permission(AppPermissions.AUDIT_SEARCH)`.

### GET /logs/audits

- Purpose: Search/paginate audit log entries (returns minimal fields per item).
- Authentication: JWT required.
- Permission: `permission.audit_logs.search`

Query parameters:
- `type` (optional): One of `Insert`, `Update`, `Delete` (case-insensitive).
- `table_name` (optional): Table name (case-insensitive).
- `start_date` (optional): ISO 8601 / RFC3339 datetime — filters records with `date_time >= start_date`.
- `end_date` (optional): ISO 8601 / RFC3339 datetime — filters records with `date_time <= end_date`.
- `user_id` (optional): User id (UUID) that performed the action.
- `page` (optional): Page number (default 1).
- `page_size` (optional): Page size (default 20).

Notes:
- FastAPI automatically parses ISO 8601 datetimes — examples: `2026-02-13T10:30:00Z` or `2026-02-13T10:30:00+00:00`.
- If provided, `start_date` and `end_date` both are nullable and can be used as an open-ended range.

Example:

```
GET /logs/audits?type=insert&table_name=users&start_date=2026-02-01T00:00:00Z&page=1&page_size=50
```

Example minimal item in list response:

```json
{
  "id": "6f1c2a9e-...",
  "table_name": "users",
  "user_id": "c3f9e2d0-...",
  "user_full_name": "Alice Example",
  "type": "Insert"
}
```

### GET /logs/audits/{id}

- Purpose: Get full audit entry details by id.
- Authentication: JWT required.
- Permission: `permission.audit_logs.view`

Path parameter:
- `id` (UUID): the audit log id.

Returns full fields including `old_values`, `new_values`, `affected_columns`, and `primary_key`.

Example:

```
GET /logs/audits/6f1c2a9e-...
```

Example detail response (abridged):

```json
{
  "id": "6f1c2a9e-...",
  "type": "Update",
  "table_name": "users",
  "date_time": "2026-02-13T10:35:00Z",
  "old_values": { "email": "old@example.com" },
  "new_values": { "email": "new@example.com" },
  "affected_columns": ["email"],
  "primary_key": { "id": "c3f9e2d0-..." },
  "user_id": "c3f9e2d0-...",
  "user_full_name": "Alice Example"
}
```

## Implementation notes

- The audit model is `app.models.audit_log.AuditLog` and is persisted in the configured logger schema.
- The service `app.services.audit_log_service.AuditLogService` performs business logic and uses `AuditLogRepository` for DB access.
- The repository uses `selectinload(AuditLog.user)` when loading details to avoid detached/ lazy-load issues.

## Security

- Do not include sensitive fields in audit records. Use `AUDIT_SENSITIVE_FIELDS` to exclude or redact sensitive data before saving.
- Ensure only authorized administrators are granted `permission.audit_logs.view` or `permission.audit_logs.search`.
