import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ENV: str
    DATABASE_URL: str
    SECRET_KEY: str
    DATABASE_ENABLED: bool = False
    
    # Token expiration settings
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    model_config = SettingsConfigDict(
        env_file=f".env.{os.getenv('ENV', 'development')}",
        env_file_encoding="utf-8"
    )

settings = Settings()
