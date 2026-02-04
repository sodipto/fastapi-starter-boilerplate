# Package Management

Guide for managing Python dependencies in the FastAPI Boilerplate project.

---

## Table of Contents

- [Overview](#overview)
- [Requirements File](#requirements-file)
- [Adding Dependencies](#adding-dependencies)
- [Updating Dependencies](#updating-dependencies)
- [Virtual Environment](#virtual-environment)
- [Dependency Groups](#dependency-groups)
- [Security Auditing](#security-auditing)
- [Best Practices](#best-practices)

---

## Overview

This project uses `pip` with a `requirements.txt` file for dependency management. All dependencies are pinned to specific versions to ensure reproducible builds across environments.

---

## Requirements File

### Current Dependencies

The main dependencies are organized by category:

```text
# Web Framework
fastapi==0.116.1
uvicorn[standard]==0.34.2

# Database
sqlalchemy[asyncio]==2.0.41
asyncpg==0.30.0          # PostgreSQL
aioodbc==0.5.0           # SQL Server

# Authentication
pyjwt==2.10.1
passlib[bcrypt]==1.7.4

# Validation
pydantic==2.11.4
pydantic-settings==2.9.1
email-validator==2.2.0

# Dependency Injection
dependency-injector==4.46.0

# Database Migrations
alembic==1.15.2

# Email
aiosmtplib==4.0.0
jinja2==3.1.6

# Caching
redis==6.2.0

# Background Jobs
apscheduler==3.11.0

# Logging
seqlog==1.0.1

# HTTP Client
httpx==0.28.1
aiohttp==3.12.6

# AWS (Optional)
boto3==1.38.30
```

---

## Adding Dependencies

### Install and Add to Requirements

```bash
# Install the package
pip install package-name

# Add to requirements.txt with version
pip freeze | grep -i package-name >> requirements.txt
```

### Manual Addition

Add the package with a pinned version:

```text
package-name==1.2.3
```

### Install All Dependencies

```bash
pip install -r requirements.txt
```

---

## Updating Dependencies

### Update Single Package

```bash
# Update package
pip install --upgrade package-name

# Update requirements.txt
pip freeze | grep -i package-name
# Then manually update the version in requirements.txt
```

### Update All Packages

```bash
# Create backup
cp requirements.txt requirements.txt.bak

# Update all packages
pip install --upgrade -r requirements.txt

# Generate new requirements
pip freeze > requirements.txt
```

### Check for Updates

```bash
# Install pip-outdated
pip install pip-outdated

# Check outdated packages
pip-outdated
```

Or use pip directly:

```bash
pip list --outdated
```

---

## Virtual Environment

### Create Virtual Environment

**Windows:**

```powershell
python -m venv .venv
.venv\Scripts\activate
```

**Linux/macOS:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Deactivate

```bash
deactivate
```

### Recreate Environment

```bash
# Remove existing
rm -rf .venv

# Create fresh
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
```

---

## Dependency Groups

### Production Dependencies

Core packages required to run the application:

| Package | Purpose |
|---------|---------|
| `fastapi` | Web framework |
| `uvicorn` | ASGI server |
| `sqlalchemy` | ORM |
| `asyncpg` / `aioodbc` | Database drivers |
| `pyjwt` | JWT handling |
| `passlib` | Password hashing |
| `pydantic` | Data validation |
| `alembic` | Migrations |

### Development Dependencies

Packages for development and testing (not in main requirements):

```bash
# Install development dependencies
pip install pytest pytest-asyncio pytest-cov httpx
pip install black isort flake8 mypy
pip install pre-commit
```

Consider creating a `requirements-dev.txt`:

```text
-r requirements.txt

# Testing
pytest==8.0.0
pytest-asyncio==0.23.0
pytest-cov==4.1.0
httpx==0.27.0

# Code Quality
black==24.0.0
isort==5.13.0
flake8==7.0.0
mypy==1.8.0

# Pre-commit
pre-commit==3.6.0
```

Install with:

```bash
pip install -r requirements-dev.txt
```

---

## Security Auditing

### Check for Vulnerabilities

```bash
# Install pip-audit
pip install pip-audit

# Scan for vulnerabilities
pip-audit
```

### Using Safety

```bash
# Install safety
pip install safety

# Check dependencies
safety check -r requirements.txt
```

### Dependabot (GitHub)

Add `.github/dependabot.yml`:

```yaml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 10
```

---

## Best Practices

### ✅ DO

1. **Pin exact versions** - Use `==` for reproducible builds
2. **Use virtual environments** - Isolate project dependencies
3. **Regularly update** - Keep dependencies current for security
4. **Audit for vulnerabilities** - Use pip-audit or safety
5. **Document changes** - Note why specific versions are pinned
6. **Test after updates** - Run full test suite after upgrades
7. **Separate dev dependencies** - Use requirements-dev.txt

### ❌ DON'T

1. **Don't use loose versions** - Avoid `>=` or no version specifier
2. **Don't commit .venv** - Add to .gitignore
3. **Don't ignore security alerts** - Address vulnerabilities promptly
4. **Don't update blindly** - Check changelogs for breaking changes

### Version Pinning Strategy

| Specifier | Example | Use Case |
|-----------|---------|----------|
| `==` | `fastapi==0.116.1` | Production (recommended) |
| `~=` | `fastapi~=0.116.0` | Allow patch updates only |
| `>=,<` | `fastapi>=0.116.0,<0.117.0` | Allow minor updates |

---

## Troubleshooting

### Dependency Conflicts

```bash
# Check for conflicts
pip check

# Install with verbose output
pip install -r requirements.txt -v
```

### Reinstall All Dependencies

```bash
# Uninstall all
pip freeze | xargs pip uninstall -y

# Reinstall
pip install -r requirements.txt
```

### Cache Issues

```bash
# Clear pip cache
pip cache purge

# Install without cache
pip install --no-cache-dir -r requirements.txt
```

---

*For more documentation, see the [docs/](.) folder.*
