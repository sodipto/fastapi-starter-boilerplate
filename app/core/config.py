import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ENV: str
    DATABASE_URL: str
    DATABASE_PROVIDER: str = "postgresql"  # Options: postgresql, mssql
    SECRET_KEY: str
    DATABASE_ENABLED: bool = False
    BACKGROUND_JOBS_ENABLED: bool = False
    
    # Logging settings
    LOG_LEVEL: str = "INFO"  # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
    
    # Token expiration settings
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Account settings
    REQUIRE_EMAIL_CONFIRMED_ACCOUNT: bool = True
    FORGOT_PASSWORD_VERIFICATION_CODE_EXPIRE_MINUTES: int = 15
    FRONTEND_URL: str = "http://localhost:3000"  # Frontend application URL

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
    S3_AWS_ACCESS_KEY_ID: str = ""
    S3_AWS_SECRET_ACCESS_KEY: str = ""
    S3_AWS_REGION: str = ""
    S3_BUCKET_NAME: str = ""
    S3_CDN_URL: str | None = None

    # Cache settings
    CACHE_TYPE: str = "memory"  # Options: memory, redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # Seq logging settings
    SEQ_ENABLED: bool = False
    SEQ_SERVER_URL: str = "http://localhost:5341"
    SEQ_API_KEY: str = ""  # Optional: Seq API key for authentication

    model_config = SettingsConfigDict(
        env_file=f".env.{os.getenv('ENV', 'development')}",
        env_file_encoding="utf-8"
    )

settings = Settings()
