
import logging
from logging.config import fileConfig

from dotenv import load_dotenv
from sqlalchemy import engine_from_config, text
from sqlalchemy import pool

from alembic import context
import os
from app.core.database.base import Base
from app.core.database.schema import ensure_schemas_exist
from app.core.database.provider import DatabaseProvider, DatabaseConfig
import importlib
import pkgutil
from app.models import __path__ as models_path

env = os.getenv("APP_ENV", "development")  # default to development
load_dotenv(f".env.{env}")

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Get database provider from environment
db_provider_str = os.getenv("DATABASE_PROVIDER", "postgresql").lower()
try:
    db_provider = DatabaseProvider(db_provider_str)
except ValueError:
    raise ValueError(
        f"Unsupported database provider: {db_provider_str}. "
        f"Supported providers are: {', '.join([p.value for p in DatabaseProvider])}"
    )

# Convert async URL to sync URL for migrations
db_url = os.getenv("DATABASE_URL")
if db_url:
    sync_url = DatabaseConfig.convert_url_for_sync(db_url, db_provider)
    config.set_main_option("sqlalchemy.url", sync_url)

# Get default schema for the provider
default_schema = DatabaseConfig.get_default_schema(db_provider)
supports_schemas = DatabaseConfig.supports_schemas(db_provider)

# Interpret the config file for Python logging.
# This line sets up loggers basically.

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

logger = logging.getLogger(__name__)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def render_item(type_, obj, autogen_context):
    """
    Custom renderer for types to ensure proper imports in migration files.
    This fixes the issue where custom types don't get properly imported.
    """
    from app.models.types.guid_type import GUID
    from app.models.types.email_status_type import EmailStatusType
    
    if type_ == "type" and isinstance(obj, GUID):
        autogen_context.imports.add("from app.models.types.guid_type import GUID")
        return "GUID()"
    
    if type_ == "type" and isinstance(obj, EmailStatusType):
        autogen_context.imports.add("from app.models.types.email_status_type import EmailStatusType")
        return f"EmailStatusType(length={obj.length})"
    
    # Fall back to default rendering
    return False


# Get all schema names from DbSchemas class
def get_target_schemas():
    """Get all schema names defined in DbSchemas."""
    from app.core.database.schema import DbSchemas
    return {value for key, value in vars(DbSchemas).items() 
            if not key.startswith("__") and isinstance(value, str)}


def include_name(name, type_, parent_names):
    """
    Filter function for autogenerate to include only our target schemas.
    This ensures Alembic properly detects tables in custom schemas.
    """
    if type_ == "schema":
        # Include our target schemas plus default schema for version table
        target_schemas = get_target_schemas()
        return name in target_schemas or name == default_schema
    return True


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_item=render_item,
    )

    with context.begin_transaction():
        context.run_migrations()


def is_autogenerate_revision() -> bool:
    """Check if we're generating a revision (autogenerate) vs running actual migrations."""
    cmd_opts = config.cmd_opts
    if cmd_opts is None:
        return False
    
    # Check if this is a revision command with autogenerate flag
    cmd = getattr(cmd_opts, 'cmd', None)
    if cmd is None:
        return False
    
    # Get the command function name
    cmd_func_name = cmd[0].__name__ if isinstance(cmd, tuple) else getattr(cmd, '__name__', str(cmd))
    
    # Check if it's a revision command (used for autogenerate)
    return cmd_func_name == 'revision'


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    
    is_autogenerate = is_autogenerate_revision()

    with connectable.connect() as connection:
        # Ensure schemas exist for proper autogenerate comparison
        # This is needed for both autogenerate and actual migrations
        if supports_schemas:
            logger.info(f"Ensuring schemas exist for {db_provider.value}")
            with connection.begin():
                ensure_schemas_exist(connection, db_provider)
        
        # Configure context based on schema support
        context_config = {
            "connection": connection,
            "target_metadata": target_metadata,
            "render_item": render_item,
        }
        if supports_schemas:
            context_config["include_schemas"] = True
            context_config["include_name"] = include_name
            if default_schema:
                context_config["version_table_schema"] = default_schema
        
        context.configure(**context_config)
        
        if is_autogenerate:
            # For autogenerate, run migrations in a transaction that gets rolled back
            # This prevents creating the alembic_version table while still allowing
            # the autogenerate comparison to work
            trans = connection.begin()
            try:
                context.run_migrations()
            finally:
                trans.rollback()
        else:
            # For actual migrations, commit the transaction
            with context.begin_transaction():
                context.run_migrations()


# Dynamically import all modules in the app.models package
for _, module_name, _ in pkgutil.iter_modules(models_path):
    importlib.import_module(f"app.models.{module_name}")

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
