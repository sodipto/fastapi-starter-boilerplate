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

    # Email settings
    MAIL_HOST: str = "smtp.gmail.com"
    MAIL_PORT: int = 587
    MAIL_USERNAME: str = ""
    MAIL_PASSWORD: str = ""
    MAIL_FROM_EMAIL: str = ""
    MAIL_FROM_NAME: str = "FastAPI App"
    MAIL_USE_TLS: bool = True
    MAIL_USE_SSL: bool = False
    ENABLE_EMAIL_LOGS: bool = True

    # AWS S3 settings
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION: str = ""
    BUCKET_NAME: str = ""
    S3_CDN_URL: str | None = None

    model_config = SettingsConfigDict(
        env_file=f".env.{os.getenv('ENV', 'development')}",
        env_file_encoding="utf-8"
    )

settings = Settings()
