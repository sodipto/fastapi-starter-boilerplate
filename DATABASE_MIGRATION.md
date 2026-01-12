# Database Migration Guide

This guide covers database migration commands using Alembic for the FastAPI Boilerplate project.

## Alembic Migration Commands

### Initialize Alembic (One-time setup)
```bash
alembic init alembic
```
This command initializes Alembic in your project. Only run this once during initial project setup.

### Create a New Migration

#### Auto-generate migration from model changes
```bash
alembic revision --autogenerate -m "MigrationName"
```
Replace `MigrationName` with a descriptive name for your migration (e.g., "add_user_table", "add_email_column").

#### Create empty migration file
```bash
alembic revision -m "MigrationName"
```
Use this when you need to write custom migration logic.

### Apply Migrations

#### Upgrade to latest version
```bash
alembic upgrade head
```
Applies all pending migrations to bring the database to the latest schema.

#### Upgrade to specific revision
```bash
alembic upgrade <revision_id>
```
Applies migrations up to a specific revision ID.

### Rollback Migrations

#### Revert the last migration
```bash
alembic downgrade -1
```
Rolls back the most recent migration.

#### Downgrade to specific revision
```bash
alembic downgrade <revision_id>
```
Rolls back to a specific revision ID.

#### Downgrade to base (remove all migrations)
```bash
alembic downgrade base
```
⚠️ **Warning:** This will revert all migrations. Use with caution!

### View Migration History

#### Show current revision
```bash
alembic current
```

#### Show migration history
```bash
alembic history
```

#### Show verbose history
```bash
alembic history --verbose
```

## Common Migration Workflow

1. **Modify your models** in `app/models/`
2. **Generate migration**:
   ```bash
   alembic revision --autogenerate -m "descriptive_migration_name"
   ```
3. **Review the migration file** in `alembic/versions/`
4. **Apply the migration**:
   ```bash
   alembic upgrade head
   ```
5. **Verify** the changes in your database

## Best Practices

- Always review auto-generated migrations before applying them
- Use descriptive migration names that explain what changed
- Test migrations in development before applying to production
- Keep your requirements.txt up to date
- Commit migration files to version control
- Never modify migrations that have been applied to production

## Troubleshooting

### Migration conflicts
If you encounter conflicts, you may need to merge migration heads:
```bash
alembic merge heads -m "merge_migrations"
```

### Reset migrations (development only)
```bash
alembic downgrade base
# Then drop all tables manually or recreate database
alembic upgrade head
```
