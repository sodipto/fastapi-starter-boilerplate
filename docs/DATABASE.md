# Database Guide

Multi-provider database support with async SQLAlchemy 2.0 and Alembic migrations.

## Table of Contents

- [Configuration](#configuration)
- [PostgreSQL Setup](#postgresql-setup)
- [SQL Server Setup](#sql-server-setup)
- [Migrations](#migrations)
- [Switching Providers](#switching-providers)
- [Troubleshooting](#troubleshooting)

---

## Configuration

Set the database provider and connection string in your `.env` file:

```env
DATABASE_ENABLED=True
DATABASE_PROVIDER=postgresql   # postgresql or mssql
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/dbname
```

---

## PostgreSQL Setup

### Connection String

```env
DATABASE_PROVIDER=postgresql
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/database_name
```

### Create Database

```bash
# Using createdb
createdb fastapi_db

# Using psql
psql -U postgres -c "CREATE DATABASE fastapi_db;"
```

### Docker

```bash
docker run -d \
  --name postgres \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=fastapi_db \
  -p 5432:5432 \
  postgres:15
```

---

## SQL Server Setup

### Prerequisites

Install ODBC Driver 17 for SQL Server:

**Windows:** [Download from Microsoft](https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server)

**Linux (Ubuntu):**

```bash
curl https://packages.microsoft.com/keys/microsoft.asc | sudo apt-key add -
curl https://packages.microsoft.com/config/ubuntu/$(lsb_release -rs)/prod.list | sudo tee /etc/apt/sources.list.d/mssql-release.list
sudo apt-get update
sudo ACCEPT_EULA=Y apt-get install -y msodbcsql17
```

### Connection String

```env
DATABASE_PROVIDER=mssql
DATABASE_URL=mssql+aioodbc://user:password@localhost:1433/database_name?driver=ODBC+Driver+17+for+SQL+Server
```

### Windows Authentication

```env
DATABASE_URL=mssql+aioodbc://localhost:1433/database_name?driver=ODBC+Driver+17+for+SQL+Server&Trusted_Connection=yes
```

### Create Database

```sql
CREATE DATABASE fastapi_db;
GO
```

---

## Migrations

Migrations work identically for both providers.

### Create Migration

```bash
# Auto-generate from model changes
alembic revision --autogenerate -m "add_users_table"

# Create empty migration
alembic revision -m "custom_migration"
```

### Apply Migrations

```bash
# Apply all pending
alembic upgrade head

# Apply to specific revision
alembic upgrade <revision_id>
```

### Rollback

```bash
# Rollback last migration
alembic downgrade -1

# Rollback to specific revision
alembic downgrade <revision_id>

# Rollback all (caution!)
alembic downgrade base
```

### View History

```bash
alembic current    # Current revision
alembic history    # Full history
```

---

## Switching Providers

1. Update `.env` with new provider and connection string
2. Run migrations: `alembic upgrade head`
3. Restart the application

> **Note:** Data must be migrated manually between providers.

---

## Connection String Examples

### PostgreSQL

```
postgresql+asyncpg://user:pass@localhost:5432/dbname
postgresql+asyncpg://user:pass@host.docker.internal:5432/dbname
postgresql+asyncpg://user:pass@postgres:5432/dbname  # Docker Compose
```

### SQL Server

```
mssql+aioodbc://user:pass@localhost:1433/dbname?driver=ODBC+Driver+17+for+SQL+Server
mssql+aioodbc://user:pass@localhost:1433/dbname?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes
```

---

## Troubleshooting

### PostgreSQL

| Error | Solution |
|-------|----------|
| `InvalidCatalogNameError` | Database doesn't exist — create it first |
| `password authentication failed` | Check credentials and `pg_hba.conf` |

### SQL Server

| Error | Solution |
|-------|----------|
| `Data source name not found` | Install ODBC Driver 17 |
| `Login failed for user` | Verify credentials or Windows auth |
| `Cannot open database` | Database doesn't exist — create it first |

---

## Schema Support

| Feature | PostgreSQL | SQL Server |
|---------|------------|------------|
| Schemas | ✅ | ✅ |
| Default Schema | `public` | `dbo` |

---

## Best Practices

1. **Use environment-specific configs** — `.env.development`, `.env.production`
2. **Backup before migrations** — `pg_dump` or `BACKUP DATABASE`
3. **Test migrations on staging first**
4. **Monitor connection pools** — adjust `pool_size` and `max_overflow`
5. **Enable SSL/TLS in production**
