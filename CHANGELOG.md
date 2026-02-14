# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- (Add new features here before release)

### Changed
- (Add changes here before release)

### Fixed
- (Add bug fixes here before release)

---

## [1.0.0] - 2026-02-14

### Added
- **Authentication System**
  - JWT access and refresh token authentication
  - Email verification with confirmation codes
  - Password reset with verification codes
  - Secure password hashing with bcrypt

- **Authorization & RBAC**
  - Role-based access control (RBAC)
  - Granular permission system
  - Role and permission seeding

- **Database Support**
  - PostgreSQL support with asyncpg
  - SQL Server support with aioodbc
  - Async SQLAlchemy 2.0 ORM
  - Alembic migrations with auto-generation

- **Caching**
  - In-memory cache provider
  - Redis cache provider
  - Automatic cache invalidation

- **Email Service**
  - Async SMTP email sending
  - Jinja2 email templates
  - Email logging and tracking

- **Background Jobs**
  - APScheduler integration
  - Job registry pattern
  - Health check job example

- **Rate Limiting**
  - Per-endpoint rate limiting
  - Configurable limits and windows
  - Exempt paths support

- **File Storage**
  - AWS S3 integration
  - MinIO integration
  - Presigned URL generation
  - CDN support

- **Audit Logging**
  - Automatic change tracking
  - User context preservation
  - Sensitive field masking

- **Logging & Monitoring**
  - Structured logging
  - Seq integration
  - Request/response logging

- **API Features**
  - OpenAPI/Swagger documentation
  - Pydantic v2 validation
  - Standardized error responses
  - API versioning (v1)

- **Developer Experience**
  - Dependency injection with dependency-injector
  - Clean architecture (Repository → Service → Controller)
  - Comprehensive documentation
  - Docker and Docker Compose setup
  - pytest test setup with async support

---

## Version History

| Version | Date | Description |
|---------|------|-------------|
| 1.0.0 | 2026-02-14 | Initial release |

---

## Versioning Guide

This project uses **Semantic Versioning (SemVer)**:

```
MAJOR.MINOR.PATCH
```

- **MAJOR**: Breaking changes (incompatible API changes)
- **MINOR**: New features (backwards compatible)
- **PATCH**: Bug fixes (backwards compatible)

### Examples:
- `1.0.0` → `2.0.0`: Breaking API changes
- `1.0.0` → `1.1.0`: New feature added
- `1.0.0` → `1.0.1`: Bug fix

### Pre-release versions:
- `1.0.0-alpha.1`: Alpha release
- `1.0.0-beta.1`: Beta release
- `1.0.0-rc.1`: Release candidate

---

## How to Update This Changelog

1. **During Development**: Add entries under `[Unreleased]`
2. **Before Release**: Move entries from `[Unreleased]` to a new version section
3. **Categories to use**:
   - `Added` - New features
   - `Changed` - Changes in existing functionality
   - `Deprecated` - Features to be removed in future
   - `Removed` - Removed features
   - `Fixed` - Bug fixes
   - `Security` - Security vulnerability fixes

[Unreleased]: https://github.com/sodipto/fastapi-starter-boilerplate/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/sodipto/fastapi-starter-boilerplate/releases/tag/v1.0.0
