from logging.config import fileConfig

from dotenv import load_dotenv
from sqlalchemy import engine_from_config, text
from sqlalchemy import pool

from alembic import context
import os
from app.core.database.base import Base
from app.core.database.schema import ensure_schemas_exist
import importlib
import pkgutil
from app.models import __path__ as models_path

env = os.getenv("APP_ENV", "development")  # default to development
load_dotenv(f".env.{env}")

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config
# Set sqlalchemy.url from environment variable if present
db_url = os.getenv("DATABASE_URL").replace("postgresql+asyncpg:","postgresql:")
if db_url:
    config.set_main_option("sqlalchemy.url", db_url)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


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
    )

    with context.begin_transaction():
        context.run_migrations()


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

    with connectable.connect() as connection:
        print(">>> Ensuring schemas exist")
        with connection.begin():
            ensure_schemas_exist(connection)
            
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_schemas=True,
            version_table_schema='public'
        )

        with context.begin_transaction():
            context.run_migrations()


# Dynamically import all modules in the app.models package
for _, module_name, _ in pkgutil.iter_modules(models_path):
    importlib.import_module(f"app.models.{module_name}")

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
