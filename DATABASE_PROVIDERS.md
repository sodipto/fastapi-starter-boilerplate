# Multi-Database Provider Support

This project now supports two database providers:
- **PostgreSQL** (default)
- **Microsoft SQL Server**

Only one database provider can be active at a time, configured via the `.env` file.

## Configuration

### 1. PostgreSQL

**Required packages:** `asyncpg`, `psycopg2-binary`

**.env configuration:**
```env
DATABASE_PROVIDER=postgresql
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/database_name
```

**Example:**
```env
DATABASE_PROVIDER=postgresql
DATABASE_URL=postgresql+asyncpg://postgres:123456@localhost:5432/fastapi_boilerplate_dev
```

**Features:**
- ✅ Full schema support
- ✅ Async operations
- ✅ Excellent performance

---

### 2. Microsoft SQL Server (MSSQL)

**Required packages:** `aioodbc`, `pyodbc`

**System Requirements:**
- ODBC Driver 17 for SQL Server (or newer)
- Windows: [Download from Microsoft](https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server)
- Linux: Follow [Microsoft's instructions](https://docs.microsoft.com/en-us/sql/connect/odbc/linux-mac/installing-the-microsoft-odbc-driver-for-sql-server)

**.env configuration:**
```env
DATABASE_PROVIDER=mssql
DATABASE_URL=mssql+aioodbc://user:password@localhost:1433/database_name?driver=ODBC+Driver+17+for+SQL+Server
```

**Example:**
```env
DATABASE_PROVIDER=mssql
DATABASE_URL=mssql+aioodbc://sa:YourStrong@Passw0rd@localhost:1433/fastapi_boilerplate_dev?driver=ODBC+Driver+17+for+SQL+Server
```

**Alternative with trusted connection (Windows Authentication):**
```env
DATABASE_URL=mssql+aioodbc://localhost:1433/fastapi_boilerplate_dev?driver=ODBC+Driver+17+for+SQL+Server&Trusted_Connection=yes
```

**Features:**
- ✅ Full schema support
- ✅ Async operations
- ✅ Enterprise features

---

## Installation

### Install Database Drivers

All required Python packages are listed in `requirements.txt`. Install them with:

```bash
pip install -r requirements.txt
```

### Driver-Specific Installation

**For SQL Server (Windows):**
1. Download and install [ODBC Driver 17 for SQL Server](https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server)

**For SQL Server (Linux/Ubuntu):**
```bash
curl https://packages.microsoft.com/keys/microsoft.asc | sudo apt-key add -
curl https://packages.microsoft.com/config/ubuntu/$(lsb_release -rs)/prod.list | sudo tee /etc/apt/sources.list.d/mssql-release.list
sudo apt-get update
sudo ACCEPT_EULA=Y apt-get install -y msodbcsql17
```

---

## Database Setup

### PostgreSQL
```bash
# Create database
createdb fastapi_boilerplate_dev

# Or using psql
psql -U postgres
CREATE DATABASE fastapi_boilerplate_dev;
```

### Microsoft SQL Server
```sql
-- Using sqlcmd or SQL Server Management Studio
CREATE DATABASE fastapi_boilerplate_dev;
GO
```

---

## Running Migrations

Migrations work the same way regardless of the database provider:

```bash
# Create a new migration
alembic revision --autogenerate -m "description"

# Run migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1
```

The migration system automatically:
- Converts async database URLs to sync URLs
- Creates schemas for PostgreSQL and SQL Server
- Uses provider-specific default schemas

---

## Switching Between Providers

To switch database providers:

1. Update your `.env` file with the new provider and connection string:
   ```env
   DATABASE_PROVIDER=mssql
   DATABASE_URL=mssql+aioodbc://sa:password@localhost:1433/mydb?driver=ODBC+Driver+17+for+SQL+Server
   ```

2. Create/migrate the database:
   ```bash
   alembic upgrade head
   ```

3. Restart your application

**Note:** You'll need to migrate your data manually if switching between existing databases.

---

## Troubleshooting

### PostgreSQL

**Error: `asyncpg.exceptions.InvalidCatalogNameError`**
- The database doesn't exist. Create it first using `createdb` or `CREATE DATABASE`.

**Error: `password authentication failed`**
- Check your username and password in the connection string
- Verify `pg_hba.conf` allows password authentication

### Microsoft SQL Server

**Error: `Data source name not found`**
- Install the ODBC Driver 17 for SQL Server
- Verify the driver name in your connection string matches the installed driver

**Error: `Login failed for user`**
- For SQL authentication: verify username and password
- For Windows authentication: ensure the service has proper permissions

**Error: `Cannot open database`**
- Create the database first using SQL Server Management Studio or sqlcmd

---

## Connection String Examples

### PostgreSQL
```
postgresql+asyncpg://user:pass@localhost:5432/dbname
postgresql+asyncpg://user:pass@host.docker.internal:5432/dbname  # Docker
postgresql+asyncpg://user:pass@postgres:5432/dbname  # Docker Compose
```

### Microsoft SQL Server
```
mssql+aioodbc://user:pass@localhost:1433/dbname?driver=ODBC+Driver+17+for+SQL+Server
mssql+aioodbc://user:pass@localhost:1433/dbname?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes
mssql+aioodbc://localhost:1433/dbname?driver=ODBC+Driver+17+for+SQL+Server&Trusted_Connection=yes
```

---

## Performance Considerations

### PostgreSQL
- Excellent performance for most workloads
- Strong support for JSON, arrays, and advanced data types
- Best choice for complex queries and transactions

### Microsoft SQL Server
- Enterprise-grade performance and features
- Excellent integration with Microsoft ecosystem
- Consider using columnstore indexes for analytical queries

---

## Schema Support

| Feature | PostgreSQL | SQL Server |
|---------|-----------|------------|
| Schemas | ✅ Yes | ✅ Yes |
| Default Schema | `public` | `dbo` |
| Multiple Schemas | ✅ Yes | ✅ Yes |

---

## Best Practices

1. **Use environment-specific .env files:**
   - `.env.development`
   - `.env.staging`
   - `.env.production`

2. **Always backup before migrations:**
   ```bash
   # PostgreSQL
   pg_dump dbname > backup.sql
   
   # SQL Server
   BACKUP DATABASE dbname TO DISK = 'backup.bak'
   ```

3. **Test migrations on a copy first:**
   - Never run migrations directly on production without testing
   - Use a staging environment with production-like data

4. **Monitor connection pools:**
   - Check `pool_size` and `max_overflow` settings
   - Adjust based on your application's concurrency needs

5. **Use connection string parameters wisely:**
   - Enable SSL/TLS for production
   - Set appropriate timeouts
