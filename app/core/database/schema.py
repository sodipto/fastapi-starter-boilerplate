import logging
from sqlalchemy.schema import CreateSchema
from sqlalchemy import text
from app.core.database.provider import DatabaseProvider

logger = logging.getLogger(__name__)

class DbSchemas:
    identity = "identity"
    logger = "logger"

def ensure_schemas_exist(engine, provider: DatabaseProvider):
    """
    Create schemas if they don't exist.
    Applicable for PostgreSQL and MSSQL.
    
    Args:
        engine: SQLAlchemy engine or connection
        provider: Database provider type
    """
    
    for schema_name in (value for key, value in vars(DbSchemas).items() if not key.startswith("__") and isinstance(value, str)):
        try:
            if provider == DatabaseProvider.MSSQL:
                # SQL Server doesn't support CREATE SCHEMA IF NOT EXISTS
                # We need to check existence first
                check_query = text(f"""
                    IF NOT EXISTS (SELECT 1 FROM sys.schemas WHERE name = '{schema_name}')
                    BEGIN
                        EXEC('CREATE SCHEMA [{schema_name}]')
                    END
                """)
                engine.execute(check_query)
            elif provider == DatabaseProvider.POSTGRESQL:
                # PostgreSQL supports IF NOT EXISTS
                engine.execute(CreateSchema(schema_name, if_not_exists=True))
        except Exception as e:
            logger.error(f"Could not create schema '{schema_name}': {e}")
