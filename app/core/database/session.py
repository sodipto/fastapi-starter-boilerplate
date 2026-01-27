from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.core.database.provider import DatabaseProvider, DatabaseConfig

# Determine the database provider
try:
    db_provider = DatabaseProvider(settings.DATABASE_PROVIDER.lower())
except ValueError:
    raise ValueError(
        f"Unsupported database provider: {settings.DATABASE_PROVIDER}. "
        f"Supported providers are: {', '.join([p.value for p in DatabaseProvider])}"
    )

# Get provider-specific engine arguments
engine_args = DatabaseConfig.get_engine_args(db_provider)

# Create the async engine with provider-specific configuration
engine = create_async_engine(settings.DATABASE_URL, **engine_args)
async_session = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session
