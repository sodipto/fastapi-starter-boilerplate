import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ENV: str
    DATABASE_URL: str
    SECRET_KEY: str
    DATABASE_ENABLED: bool = False

    model_config = SettingsConfigDict(
        env_file=f".env.{os.getenv('ENV', 'development')}",
        env_file_encoding="utf-8"
    )

settings = Settings()
