# 🚀 Python FastAPI Starter Boilerplate

A robust, production-ready FastAPI boilerplate designed for rapid API development with modern best practices, dependency injection, modular architecture, and comprehensive error handling.

![FastAPI](https://img.shields.io/badge/FastAPI-0.116.1-009688?style=for-the-badge&logo=fastapi)
![Python](https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0.41-red?style=for-the-badge&logo=sqlalchemy)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Supported-blue?style=for-the-badge&logo=postgresql)
![MSSQL](https://img.shields.io/badge/SQL_Server-Supported-red?style=for-the-badge&logo=microsoftsqlserver)
![Docker](https://img.shields.io/badge/Docker-Ready-blue?style=for-the-badge&logo=docker)

## ✨ Features

- 🔐 **JWT Authentication** - Secure token-based authentication and support refresh token
- 🏗️ **Dependency Injection** - Clean architecture with dependency-injector
- 📊 **Multi-Database Support** - PostgreSQL and SQL Server with async SQLAlchemy 2.0
- 🔄 **Database Migrations** - Alembic for schema management across all providers
- 🛡️ **Error Handling** - Comprehensive exception middleware
- 📝 **API Documentation** - Auto-generated Swagger/OpenAPI docs
- 🐳 **Docker Support** - Containerized deployment ready
- 🔧 **Environment Configuration** - Multi-environment setup
- 🧪 **Modular Architecture** - Clean separation of concerns
- 🔒 **Security** - Password hashing with bcrypt
- ⚡ **Async/Await** - Full async support throughout

## 📁 Project Structure

```
python-fastapi-boilerplate/
├── 📁 alembic/                          # Database migrations
│   ├── 📄 env.py                        # Alembic environment configuration
│   ├── 📄 README                        # Migration documentation
│   ├── 📄 script.py.mako                # Migration template
│   └── 📁 versions/                     # Migration files
│       └── 📄 0541f9ea1a26_create_users_table.py
│
├── 📁 app/                              # Main application package
│   ├── 📁 api/                          # API layer
│   │   └── 📁 endpoints/                       # API version 1
│   │       ├── 📁 v1/            # API endpoints
│   │       │   ├── 📄 auth.py           # Authentication endpoints
│   │       │   └── 📄 user.py           # User management endpoints
│   │       └── 📄 routes.py             # Route aggregation
│   │
│   ├── 📁 core/                         # Core application components
│   │   ├── 📄 config.py                 # Application configuration
│   │   ├── 📄 container.py              # Dependency injection container
│   │   ├── 📁 database/                 # Database layer
│   │   │   ├── 📄 base.py               # Base database configuration
│   │   │   ├── 📄 migrate.py            # Migration utilities
│   │   │   ├── 📄 schema.py             # Database schema definitions
│   │   │   └── 📄 session.py            # Database session management
│   │   ├── 📄 identity.py               # Identity management
│   │   ├── 📄 jwt_security.py           # JWT security utilities
│   │   ├── 📁 middlewares/              # Custom middlewares
│   │   │   ├── 📄 __init__.py
│   │   │   ├── 📄 exception_middleware.py
│   │   │   ├── 📄 validation_exception_handler.py
│   │   │   └── 📄 validation_exception_middleware.py
│   │   └── 📄 open_api.py               # OpenAPI customization
│   │
│   ├── 📄 main.py                       # Application entry point
│   │
│   ├── 📁 models/                       # SQLAlchemy models
│   │   ├── 📄 __init__.py
│   │   └── 📄 user.py                   # User model
│   │
│   ├── 📁 repositories/                 # Data access layer
│   │   ├── 📄 __init__.py
│   │   └── 📄 user_repository.py        # User data operations
│   │
│   ├── 📁 schema/                       # Pydantic schemas
│   │   ├── 📄 __init__.py
│   │   ├── 📁 request/                  # Request schemas
│   │   │   └── 📁 auth/
│   │   │       └── 📄 login_request.py
│   │   └── 📁 response/                 # Response schemas
│   │       └── 📄 error_schema.py
│   │
│   ├── 📁 services/                     # Business logic layer
│   │   ├── 📄 __init__.py
│   │   ├── 📄 auth_service.py           # Authentication business logic
│   │   └── 📄 user_service.py           # User management business logic
│   │
│   └── 📁 utils/                        # Utility functions
│       ├── 📄 auth_utils.py             # Authentication utilities
│       └── 📄 exception_utils.py        # Exception handling utilities
│
├── 📄 alembic.ini                       # Alembic configuration
├── 📄 command.txt                       # Development commands
├── 📄 Dockerfile                        # Docker configuration
├── 📄 requirements.txt                  # Python dependencies
└── 📄 test_asyncpg.py                   # Database connection test
```

## 🏗️ Architecture Overview

This boilerplate follows a **Clean Architecture** pattern with clear separation of concerns:

### **Layers:**

1. **API Layer** (`app/api/`) - HTTP endpoints and request/response handling
2. **Service Layer** (`app/services/`) - Business logic and orchestration
3. **Repository Layer** (`app/repositories/`) - Data access and persistence
4. **Model Layer** (`app/models/`) - Database models and entities
5. **Core Layer** (`app/core/`) - Configuration, DI container, and utilities

### **Key Design Patterns:**

- **Dependency Injection** - Using `dependency-injector` for clean dependency management
- **Repository Pattern** - Abstracting data access logic
- **Service Layer Pattern** - Centralizing business logic
- **Middleware Pattern** - Cross-cutting concerns like error handling

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- One of the supported databases:
  - PostgreSQL 12+ (recommended)
  - Microsoft SQL Server 2019+
- Docker (optional)

### 1. Clone and Setup

```bash
git clone <your-repo-url>
cd python-fastapi-boilerplate
```

### 2. Environment Configuration

Create environment files for different environments:

```bash
# Development
cp .env.development.example .env.development

# Production
cp .env.production.example .env.production
```

Example `.env.development`:
```env
ENV=development
DATABASE_PROVIDER=postgresql
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/fastapi_boilerplate
SECRET_KEY=your-super-secret-key-here
```

**For other databases, see [DATABASE_PROVIDERS.md](DATABASE_PROVIDERS.md) for detailed configuration.**

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Database Setup

```bash
# Run migrations
alembic upgrade head

# Or run migrations programmatically (handled in main.py)
```

### 5. Run the Application

```bash
# Development
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 6. Access Documentation

- **Swagger UI**: http://localhost:8000/swagger
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### 7. Health Check

The application provides a health check endpoint for monitoring and container orchestration:

- **Endpoint**: `GET /health`
- **Response**: `{"status": "healthy"}`

> **Note**: This endpoint is excluded from Swagger documentation.

## 🐳 Docker Deployment

### Build and Run with Docker

```bash
# Build the image
docker build -t fastapi-starter-boilerplate .

# Run the container
docker run -p 8000:8000 --env-file .env.development fastapi-starter-boilerplate
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ENV` | Environment (development/production) | `development` |
| `DATABASE_PROVIDER` | Database type (postgresql/mssql) | `postgresql` |
| `DATABASE_URL` | Database connection string | Required |
| `SECRET_KEY` | JWT secret key | Required |

### Database Configuration

The application supports **PostgreSQL** and **Microsoft SQL Server** with async SQLAlchemy 2.0.

**Quick Start Examples:**

```bash
# PostgreSQL (default)
DATABASE_PROVIDER=postgresql
DATABASE_URL=postgresql+asyncpg://username:password@localhost:5432/database_name

# Microsoft SQL Server
DATABASE_PROVIDER=mssql
DATABASE_URL=mssql+aioodbc://username:password@localhost:1433/database_name?driver=ODBC+Driver+17+for+SQL+Server
```

**📖 For comprehensive database setup guides, troubleshooting, and advanced configuration, see [DATABASE_PROVIDERS.md](DATABASE_PROVIDERS.md)**

## 🛠️ Development

### Adding New Endpoints

1. **Create endpoint file** in `app/api/v1/endpoints/`
2. **Add to routes** in `app/api/v1/routes.py`
3. **Create schemas** in `app/schema/`
4. **Add service methods** in `app/services/`
5. **Update container** in `app/core/container.py`

### Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "migration_name"

# Apply migrations for update database
alembic upgrade head

# Rollback migration
alembic downgrade -1
```
**Built with ❤️ using FastAPI and modern Python practices**
