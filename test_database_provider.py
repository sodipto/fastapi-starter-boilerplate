"""
Test database connectivity for different providers.
This script helps verify that the database configuration is correct.
"""
import asyncio
import sys
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

from app.core.config import settings
from app.core.database.provider import DatabaseProvider, DatabaseConfig


async def test_connection():
    """Test database connection for the configured provider."""
    
    print("=" * 70)
    print("Database Connection Test")
    print("=" * 70)
    
    # Get provider
    try:
        db_provider = DatabaseProvider(settings.DATABASE_PROVIDER.lower())
        print(f"\n✓ Database Provider: {db_provider.value.upper()}")
    except ValueError as e:
        print(f"\n✗ Error: {e}")
        return False
    
    # Display connection info
    print(f"✓ Database URL: {settings.DATABASE_URL[:50]}...")
    print(f"✓ Database Enabled: {settings.DATABASE_ENABLED}")
    
    # Get engine configuration
    engine_args = DatabaseConfig.get_engine_args(db_provider)
    print(f"✓ Engine Configuration: {engine_args}")
    
    # Check schema support
    supports_schemas = DatabaseConfig.supports_schemas(db_provider)
    print(f"✓ Schema Support: {'Yes' if supports_schemas else 'No (uses databases)'}")
    
    if supports_schemas:
        default_schema = DatabaseConfig.get_default_schema(db_provider)
        print(f"✓ Default Schema: {default_schema}")
    
    print("\n" + "-" * 70)
    print("Testing connection...")
    print("-" * 70 + "\n")
    
    try:
        # Create engine
        engine = create_async_engine(settings.DATABASE_URL, **engine_args)
        
        # Test connection
        async with engine.begin() as conn:
            # Simple query to test connectivity
            result = await conn.execute(text("SELECT 1"))
            row = result.fetchone()
            
            if row and row[0] == 1:
                print("✓ Connection successful!")
                
                # Get database version
                version_queries = {
                    DatabaseProvider.POSTGRESQL: "SELECT version()",
                    DatabaseProvider.MSSQL: "SELECT @@VERSION",
                }
                
                if db_provider in version_queries:
                    result = await conn.execute(text(version_queries[db_provider]))
                    version = result.fetchone()[0]
                    print(f"\n✓ Database Version:")
                    print(f"  {version.split('\\n')[0][:100]}")
                
                # Test schema creation (if supported)
                if supports_schemas:
                    print(f"\n✓ Schema support is available")
                    try:
                        # Try to create a test schema
                        await conn.execute(text("CREATE SCHEMA IF NOT EXISTS test_schema"))
                        print(f"  - Created/verified test_schema")
                        
                        # Clean up
                        await conn.execute(text("DROP SCHEMA IF EXISTS test_schema"))
                        print(f"  - Cleaned up test_schema")
                    except Exception as e:
                        print(f"  ⚠ Schema test warning: {e}")
                else:
                    print(f"\n⚠ This provider uses databases instead of schemas")
                
                print("\n" + "=" * 70)
                print("✓ All tests passed! Database is ready to use.")
                print("=" * 70)
                return True
            else:
                print("✗ Connection test failed: Unexpected result")
                return False
                
        await engine.dispose()
        
    except Exception as e:
        print(f"\n✗ Connection failed!")
        print(f"Error: {type(e).__name__}")
        print(f"Details: {str(e)}\n")
        
        # Provider-specific troubleshooting hints
        print("Troubleshooting hints:")
        print("-" * 70)
        
        if db_provider == DatabaseProvider.POSTGRESQL:
            print("PostgreSQL:")
            print("  1. Ensure PostgreSQL server is running")
            print("  2. Verify the database exists: createdb <database_name>")
            print("  3. Check credentials and connection string")
            print("  4. Verify pg_hba.conf allows connections")
            
        elif db_provider == DatabaseProvider.MSSQL:
            print("Microsoft SQL Server:")
            print("  1. Ensure SQL Server is running and accepting connections")
            print("  2. Install ODBC Driver 17 for SQL Server")
            print("  3. Verify the database exists")
            print("  4. Check authentication (SQL or Windows)")
            print("  5. Ensure TCP/IP protocol is enabled in SQL Server Configuration")
        
        print("=" * 70)
        return False


def main():
    """Run the connection test."""
    if not settings.DATABASE_ENABLED:
        print("\n⚠ Warning: DATABASE_ENABLED is set to False in .env file")
        print("Set DATABASE_ENABLED=True to enable database features\n")
    
    try:
        success = asyncio.run(test_connection())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
