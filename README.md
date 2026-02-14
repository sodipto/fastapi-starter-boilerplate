<div align="center">

# 🚀 FastAPI Production Boilerplate

**A batteries-included FastAPI starter template for building scalable, production-ready APIs**

Stop reinventing the wheel. Start building features that matter.

[![FastAPI](https://img.shields.io/badge/FastAPI-0.116.1-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-D71F00?style=for-the-badge)](https://sqlalchemy.org/)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![Version](https://img.shields.io/badge/Version-1.0.0-blue?style=for-the-badge)](CHANGELOG.md)

[Features](#-features) • [Quick Start](#-quick-start) • [Documentation](#-documentation) • [Contributing](#-contributing)

</div>

---

## 💡 What Problem Does This Solve?

Building a production-ready API from scratch is time-consuming. You need authentication, authorization, database setup, caching, background jobs, email services, logging, and more—before writing a single line of business logic.

**This boilerplate gives you all of that out of the box**, so you can focus on what makes your application unique.

### Perfect for:
- 🏢 **Enterprise applications** requiring RBAC and audit logging
- 🚀 **Startups** needing to ship fast without sacrificing quality
- 📚 **Learning** FastAPI best practices and clean architecture
- 🔧 **Microservices** with standardized patterns

---

## ✨ Features

| Category | Features |
|----------|----------|
| **🔐 Authentication** | JWT access/refresh tokens, email verification, password reset |
| **🛡️ Authorization** | Role-based access control (RBAC) with granular permissions |
| **🗄️ Database** | PostgreSQL & SQL Server support, async SQLAlchemy 2.0, Alembic migrations |
| **⚡ Caching** | In-memory or Redis with automatic cache invalidation |
| **📧 Email** | Async SMTP with Jinja2 templates |
| **📋 Background Jobs** | APScheduler for scheduled tasks |
| **📝 Audit Logging** | Track all data changes with user context |
| **🚦 Rate Limiting** | Per-endpoint configurable limits |
| **📁 File Storage** | AWS S3 and MinIO support with presigned URLs |
| **📊 Logging** | Structured logging with Seq integration |
| **🧪 Testing** | pytest with async support, fixtures, and test utilities |
| **🐳 Docker** | Production-ready Docker & Docker Compose setup |

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| **Framework** | FastAPI with async/await |
| **Database** | PostgreSQL or SQL Server |
| **ORM** | SQLAlchemy 2.0 (async) |
| **Migrations** | Alembic |
| **Authentication** | python-jose (JWT) |
| **Validation** | Pydantic v2 |
| **DI Container** | dependency-injector |
| **Caching** | Redis / In-memory |
| **Email** | aiosmtplib + Jinja2 |
| **Background Jobs** | APScheduler |
| **Testing** | pytest + pytest-asyncio |
| **Logging** | Python logging + Seq |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 12+ or SQL Server 2019+
- Redis (optional, for distributed caching)

### Installation

**1. Clone the repository**

```bash
git clone https://github.com/sodipto/fastapi-starter-boilerplate.git
cd fastapi-starter-boilerplate
```

**2. Create virtual environment**

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/macOS
python3 -m venv .venv
source .venv/bin/activate
```

**3. Install dependencies**

```bash
pip install -r requirements.txt
```

**4. Configure environment**

```bash
cp .env.development .env.development
```

Edit `.env.development` with your settings:

```env
ENV=development
DATABASE_ENABLED=True
DATABASE_PROVIDER=postgresql
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/your_database
SECRET_KEY=your-secret-key-min-32-characters
```

**5. Run database migrations**

```bash
alembic upgrade head
```

**6. Start the server**

```bash
uvicorn app.main:app --reload
```

**7. Open API docs**

Navigate to http://localhost:8000/docs

---

## 📂 Project Structure

```
fastapi-starter-boilerplate/
├── app/
│   ├── api/
│   │   └── endpoints/
│   │       └── v1/           # Versioned API endpoints
│   │           ├── auth.py   # Authentication routes
│   │           ├── user.py   # User management
│   │           ├── role.py   # Role management
│   │           └── ...
│   ├── core/
│   │   ├── config.py         # Application settings
│   │   ├── container.py      # Dependency injection container
│   │   ├── database/         # Database configuration & sessions
│   │   ├── middlewares/      # Custom middlewares
│   │   ├── rbac/             # Role-based access control
│   │   └── seeders/          # Database seeders
│   ├── models/               # SQLAlchemy ORM models
│   ├── repositories/         # Data access layer
│   ├── schema/               # Pydantic request/response schemas
│   │   ├── request/
│   │   └── response/
│   ├── services/             # Business logic layer
│   ├── jobs/                 # Background job definitions
│   ├── templates/
│   │   └── emails/           # Jinja2 email templates
│   └── utils/                # Utility functions
├── alembic/                  # Database migrations
├── docs/                     # Extended documentation
├── tests/                    # Test suite
├── docker-compose.yml        # Docker Compose configuration
├── Dockerfile                # Docker image definition
├── .env.development          # Development environment variables
├── .env.production           # Production environment variables
├── .env.staging              # Staging environment variables
└── requirements.txt          # Python dependencies
```

---

## 🔌 API Endpoints

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/auth/signup` | Register new user |
| `POST` | `/api/v1/auth/login` | Authenticate user |
| `POST` | `/api/v1/auth/refresh-token` | Refresh access token |
| `POST` | `/api/v1/auth/confirm-email` | Confirm email address |
| `POST` | `/api/v1/auth/forgot-password` | Request password reset |
| `POST` | `/api/v1/auth/reset-password` | Reset password |

### Profile (Current User)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/profile` | Get current user profile |
| `PUT` | `/api/v1/profile` | Update current user profile |
| `PUT` | `/api/v1/profile/password` | Change password |

### Users Management

| Method | Endpoint | Description | Permission |
|--------|----------|-------------|------------|
| `GET` | `/api/v1/users` | Search users with pagination | `users.search` |
| `POST` | `/api/v1/users` | Create new user | `users.create` |
| `GET` | `/api/v1/users/{id}` | Get user by ID | `users.view` |
| `PUT` | `/api/v1/users/{id}` | Update user | `users.update` |
| `DELETE` | `/api/v1/users/{id}` | Delete user | `users.delete` |
| `GET` | `/api/v1/users/{id}/roles` | Get user roles | `users.view` |
| `PATCH` | `/api/v1/users/{id}/status` | Update user status | `users.update` |

### Roles Management

| Method | Endpoint | Description | Permission |
|--------|----------|-------------|------------|
| `GET` | `/api/v1/roles/permissions` | Get all available permissions | — |
| `GET` | `/api/v1/roles/search` | Search roles with pagination | `roles.search` |
| `POST` | `/api/v1/roles` | Create new role | `roles.create` |
| `GET` | `/api/v1/roles/{id}` | Get role by ID | `roles.view` |
| `PUT` | `/api/v1/roles/{id}` | Update role | `roles.update` |
| `DELETE` | `/api/v1/roles/{id}` | Delete role | `roles.delete` |

> 📖 See Swagger UI at `/docs` for complete API documentation.

---

## ⚙️ Environment Variables

### Core Settings

| Variable | Description | Default |
|----------|-------------|---------|
| `ENV` | Environment (`development`, `production`) | `development` |
| `SECRET_KEY` | JWT signing key (min 32 chars) | **Required** |
| `DATABASE_URL` | Database connection string | **Required** |
| `DATABASE_PROVIDER` | `postgresql` or `mssql` | `postgresql` |
| `DATABASE_ENABLED` | Enable database connection | `False` |

### Authentication

| Variable | Description | Default |
|----------|-------------|---------|
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token TTL | `15` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token TTL | `7` |
| `REQUIRE_EMAIL_CONFIRMED_ACCOUNT` | Require email verification | `True` |

### Caching & Performance

| Variable | Description | Default |
|----------|-------------|---------|
| `CACHE_TYPE` | `memory` or `redis` | `memory` |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379` |
| `RATE_LIMIT_ENABLED` | Enable rate limiting | `True` |
| `RATE_LIMIT_REQUESTS` | Max requests per window | `100` |

### Email

| Variable | Description | Default |
|----------|-------------|---------|
| `MAIL_HOST` | SMTP server | `smtp.gmail.com` |
| `MAIL_PORT` | SMTP port | `587` |
| `MAIL_USERNAME` | SMTP username | **Required** |
| `MAIL_PASSWORD` | SMTP password | **Required** |
| `MAIL_FROM_EMAIL` | Sender email | **Required** |

### Storage (AWS S3 / MinIO)

| Variable | Description | Default |
|----------|-------------|---------|
| `STORAGE_PROVIDER` | `aws` or `minio` | `aws` |
| `S3_BUCKET_NAME` | S3 bucket name | — |
| `MINIO_ENDPOINT` | MinIO server URL | — |

### Logging & Monitoring

| Variable | Description | Default |
|----------|-------------|---------|
| `LOG_LEVEL` | Logging level | `INFO` |
| `SEQ_ENABLED` | Enable Seq logging | `False` |
| `AUDIT_ENABLED` | Enable audit logging | `True` |

> 📄 See `.env.development` for the complete list of configuration options.

---

## 🐳 Docker

### Using Docker Compose (Recommended)

```bash
# Start all services (app, PostgreSQL, Redis)
docker-compose up -d

# View logs
docker-compose logs -f app

# Stop services
docker-compose down
```

### Manual Docker Build

```bash
# Build image
docker build -t fastapi-boilerplate .

# Run container
docker run -p 8000:8000 --env-file .env.production fastapi-boilerplate
```

---

## 📖 Commands Reference

```bash
# Development server with hot reload
uvicorn app.main:app --reload

# Production server
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Database migrations
alembic upgrade head              # Apply all migrations
alembic revision --autogenerate -m "description"  # Create migration
alembic downgrade -1              # Rollback last migration
alembic history                   # View migration history
```

---

## 📚 Documentation

| Topic | Description |
|-------|-------------|
| [Architecture](docs/ARCHITECTURE.md) | System design and patterns |
| [REST API Conventions](docs/REST_API_CONVENTIONS.md) | API design standards |
| [Authentication](docs/AUTHENTICATION.md) | JWT and security |
| [Database](docs/DATABASE.md) | Multi-database setup |
| [RBAC](docs/RBAC.md) | Permissions and roles |
| [Email Service](docs/EMAIL_SERVICE.md) | Email configuration |
| [Cache](docs/CACHE.md) | Caching strategies |
| [Background Jobs](docs/BACKGROUND_JOBS.md) | Scheduled tasks |
| [Logging](docs/LOGGING.md) | Structured logging |
| [Audit Logs](docs/AUDIT_LOGS.md) | Change tracking |
| [Testing](docs/TESTING.md) | Test setup |
| [Storage](docs/STORAGE.md) | File storage |

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

See [CHANGELOG.md](CHANGELOG.md) for version history and release notes.

---

<div align="center">

**⭐ Star this repo if you find it helpful!**

Made with ❤️ by [Sodipto Saha](https://github.com/sodipto)

</div>

