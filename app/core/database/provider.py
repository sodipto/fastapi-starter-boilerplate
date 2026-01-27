"""
Database provider utilities for multi-database support.
Handles PostgreSQL, MySQL, and Microsoft SQL Server.
"""
from enum import Enum
from typing import Dict, Any


class DatabaseProvider(str, Enum):
    """Supported database providers."""
    POSTGRESQL = "postgresql"
    MSSQL = "mssql"


class DatabaseConfig:
    """Database provider-specific configuration."""
    
    # Dialect mapping for async and sync connections
    ASYNC_DIALECTS: Dict[DatabaseProvider, str] = {
        DatabaseProvider.POSTGRESQL: "postgresql+asyncpg",
        DatabaseProvider.MSSQL: "mssql+aioodbc",
    }
    
    SYNC_DIALECTS: Dict[DatabaseProvider, str] = {
        DatabaseProvider.POSTGRESQL: "postgresql",
        DatabaseProvider.MSSQL: "mssql+pyodbc",
    }
    
    # Engine arguments specific to each provider
    ENGINE_ARGS: Dict[DatabaseProvider, Dict[str, Any]] = {
        DatabaseProvider.POSTGRESQL: {
            "echo": True,
            "pool_pre_ping": True,
        },
        DatabaseProvider.MSSQL: {
            "echo": True,
            "pool_pre_ping": True,
            # For MSSQL with pyodbc, we need to use NullPool or configure properly
            "pool_size": 5,
            "max_overflow": 10,
        },
    }

    @staticmethod
    def convert_url_for_sync(url: str, provider: DatabaseProvider) -> str:
        """
        Convert async database URL to sync URL for migrations.
        
        Args:
            url: The async database URL
            provider: The database provider type
            
        Returns:
            Sync database URL
        """
        async_dialect = DatabaseConfig.ASYNC_DIALECTS[provider]
        sync_dialect = DatabaseConfig.SYNC_DIALECTS[provider]
        
        if async_dialect in url:
            return url.replace(async_dialect, sync_dialect)
        return url

    @staticmethod
    def get_engine_args(provider: DatabaseProvider) -> Dict[str, Any]:
        """
        Get engine configuration arguments for the specified provider.
        
        Args:
            provider: The database provider type
            
        Returns:
            Dictionary of engine configuration arguments
        """
        return DatabaseConfig.ENGINE_ARGS.get(provider, {})

    @staticmethod
    def supports_schemas(provider: DatabaseProvider) -> bool:
        """
        Check if the database provider supports schemas.
        
        Args:
            provider: The database provider type
            
        Returns:
            True if schemas are supported, False otherwise
        """
        # Both PostgreSQL and SQL Server support schemas
        return provider in [DatabaseProvider.POSTGRESQL, DatabaseProvider.MSSQL]

    @staticmethod
    def get_default_schema(provider: DatabaseProvider) -> str:
        """
        Get the default schema name for the provider.
        
        Args:
            provider: The database provider type
            
        Returns:
            Default schema name
        """
        schema_map = {
            DatabaseProvider.POSTGRESQL: "public",
            DatabaseProvider.MSSQL: "dbo",
        }
        return schema_map.get(provider)
