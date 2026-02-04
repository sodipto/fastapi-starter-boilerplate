# FastAPI Starter Boilerplate

A production-ready FastAPI boilerplate with JWT authentication, role-based access control, multi-database support, and modular architecture.

![FastAPI](https://img.shields.io/badge/FastAPI-0.116.1-009688?style=flat-square&logo=fastapi)
![Python](https://img.shields.io/badge/Python-3.11+-blue?style=flat-square&logo=python)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-red?style=flat-square)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Supported-blue?style=flat-square&logo=postgresql)
![SQL Server](https://img.shields.io/badge/SQL_Server-Supported-red?style=flat-square&logo=microsoftsqlserver)

## Tech Stack

- **Framework:** FastAPI with async/await
- **Database:** PostgreSQL or SQL Server (async SQLAlchemy 2.0)
- **Authentication:** JWT with refresh tokens
- **Authorization:** Role-based access control (RBAC)
- **Migrations:** Alembic
- **DI Container:** dependency-injector
- **Caching:** In-memory or Redis
- **Email:** aiosmtplib with Jinja2 templates
- **Background Jobs:** APScheduler
- **Logging:** Structured logging with Seq support

## Prerequisites

- Python 3.11+
- PostgreSQL 12+ or SQL Server 2019+
- Redis (optional, for distributed caching)

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/sodipto/python-fastapi-boilerplate.git
cd python-fastapi-boilerplate
```

### 2. Create Virtual Environment

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

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

Copy and edit the environment file:

```bash
cp .env.development .env.development
```

Minimum required settings:

```env
ENV=development
DATABASE_ENABLED=True
DATABASE_PROVIDER=postgresql
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/your_database
SECRET_KEY=your-secret-key-min-32-characters
```

### 5. Run Migrations

```bash
alembic upgrade head
```

### 6. Start the Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 7. Access API Documentation

| Interface | URL |
|-----------|-----|
| Swagger UI | http://localhost:8000/swagger |
| ReDoc | http://localhost:8000/redoc |
| OpenAPI JSON | http://localhost:8000/openapi.json |

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ENV` | Environment name | `development` |
| `DATABASE_ENABLED` | Enable database | `False` |
| `DATABASE_PROVIDER` | `postgresql` or `mssql` | `postgresql` |
| `DATABASE_URL` | Database connection string | — |
| `SECRET_KEY` | JWT signing key | — |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token TTL | `15` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token TTL | `7` |
| `REQUIRE_EMAIL_CONFIRMED_ACCOUNT` | Require email verification | `True` |
| `FRONTEND_URL` | Frontend app URL for email links | `http://localhost:3000` |
| `CACHE_TYPE` | `memory` or `redis` | `memory` |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379` |
| `BACKGROUND_JOBS_ENABLED` | Enable scheduled jobs | `False` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `SEQ_ENABLED` | Enable Seq logging | `False` |

See `.env.development` for the full list of configuration options.

## Commands

```bash
# Development server
uvicorn app.main:app --reload

# Production server
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Create migration
alembic revision --autogenerate -m "migration_name"

# Apply migrations
alembic upgrade head

# Rollback last migration
alembic downgrade -1

# View migration history
alembic history
```

## Project Structure

```
├── app/
│   ├── api/endpoints/       # API route handlers
│   ├── core/                # Configuration, DI, middleware, RBAC
│   ├── models/              # SQLAlchemy models
│   ├── repositories/        # Data access layer
│   ├── schema/              # Pydantic request/response schemas
│   ├── services/            # Business logic
│   ├── templates/emails/    # Jinja2 email templates
│   ├── jobs/                # Background job definitions
│   └── utils/               # Utilities and helpers
├── alembic/                 # Database migrations
├── docs/                    # Extended documentation
└── requirements.txt
```

## API Endpoints

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/signup` | Register new user |
| POST | `/api/v1/auth/login` | Authenticate user |
| POST | `/api/v1/auth/refresh-token` | Refresh access token |
| POST | `/api/v1/auth/confirm-email` | Confirm email address |
| POST | `/api/v1/auth/resend-confirmation` | Resend confirmation email |
| POST | `/api/v1/auth/forgot-password` | Request password reset |
| POST | `/api/v1/auth/reset-password` | Reset password |

### Users, Roles, Profile

See Swagger UI for complete endpoint documentation.

## Docker

```bash
# Build image
docker build -t fastapi-boilerplate .

# Run container
docker run -p 8000:8000 --env-file .env.production fastapi-boilerplate
```

## Documentation

| Topic | File |
|-------|------|
| Architecture | [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) |
| REST API Conventions | [docs/REST_API_CONVENTIONS.md](docs/REST_API_CONVENTIONS.md) |
| Authentication | [docs/AUTHENTICATION.md](docs/AUTHENTICATION.md) |
| Database | [docs/DATABASE.md](docs/DATABASE.md) |
| RBAC | [docs/RBAC.md](docs/RBAC.md) |
| Exceptions | [docs/EXCEPTIONS.md](docs/EXCEPTIONS.md) |
| Email Service | [docs/EMAIL_SERVICE.md](docs/EMAIL_SERVICE.md) |
| Cache | [docs/CACHE.md](docs/CACHE.md) |
| Background Jobs | [docs/BACKGROUND_JOBS.md](docs/BACKGROUND_JOBS.md) |
| Logging | [docs/LOGGING.md](docs/LOGGING.md) |

## License

This project is open source and released under the MIT License.  
Developed and maintained by Sodipto Saha.

Copyright (c) 2026 Sodipto Saha
