# Audit Settings

This document explains the audit-related configuration used by the project.

## Environment variables

- `AUDIT_ENABLED` (bool): Enable or disable audit logging. Defaults to `True` in the example env files.
- `AUDIT_SENSITIVE_FIELDS` (comma-separated string or list): Fields to exclude or mask from audit payloads.

Examples (in `.env.*`):

```
AUDIT_ENABLED=True
AUDIT_SENSITIVE_FIELDS=password,refresh_token,tokens
```

## How the application reads these values

The project uses `pydantic-settings` (`Settings` in `app.core.config`) to load environment variables.

- `AUDIT_SENSITIVE_FIELDS` accepts either a comma-separated string (from `.env`) or a Python list.
- A validator in `app.core.config.Settings` normalizes the value to a Python `list[str]` so the rest of the code can rely on a list.

## Usage

Use `settings.AUDIT_SENSITIVE_FIELDS` in your audit logic to mask or exclude fields when recording payloads.

Example:

```python
from app.core.config import settings

for key in settings.AUDIT_SENSITIVE_FIELDS:
    if key in payload:
        payload[key] = "[REDACTED]"
```

## Notes

- You can configure different sensitive fields per environment by changing the `.env.development`, `.env.staging`, and `.env.production` files.
- If you provide a JSON list in an environment variable (e.g. `["a","b"]`), `pydantic-settings` will parse it as a list automatically.
