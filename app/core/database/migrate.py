import os
from logging.config import fileConfig

from alembic import command
from alembic.config import Config
from dotenv import load_dotenv
from app.core.config import settings


def run_pending_migrations():
    # Path to your alembic.ini
    alembic_cfg = Config("alembic.ini")
    
    # Optional: dynamically set DB URL from env if needed
    load_dotenv(dotenv_path=f".env.{os.getenv('APP_ENV', 'development')}")

    # Set sqlalchemy.url manually from env
    alembic_cfg.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

    # Apply all migrations
    command.upgrade(alembic_cfg, "head")
