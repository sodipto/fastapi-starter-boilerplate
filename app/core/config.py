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
    EMAIL_VERIFICATION_CODE_EXPIRE_MINUTES: int = 60
    FRONTEND_URL: str = "http://localhost:3000"  # Frontend application URL

    # Email settings
    MAIL_HOST: str = "smtp.gmail.com"
    MAIL_PORT: int = 587
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM_EMAIL: str
    MAIL_FROM_NAME: str = "FastAPI App"
    MAIL_USE_TLS: bool = True
    MAIL_USE_SSL: bool = False
    ENABLE_EMAIL_LOGS: bool = True

    # Storage provider settings
    STORAGE_PROVIDER: str = "aws"  # Options: aws, minio
    PRESIGNED_URL_EXPIRE_MINUTES: int = 10  # Expiration time for presigned URLs when CDN is not configured
    
    # AWS S3 settings (used when STORAGE_PROVIDER=aws)
    S3_AWS_ACCESS_KEY_ID: str | None = None
    S3_AWS_SECRET_ACCESS_KEY: str | None = None
    S3_AWS_REGION: str | None = None
    S3_BUCKET_NAME: str | None = None
    S3_CDN_URL: str | None = None
    
    # MinIO settings (used when STORAGE_PROVIDER=minio)
    MINIO_ENDPOINT: str | None = None  # e.g., localhost:9000 or minio.example.com:9000
    MINIO_ACCESS_KEY: str | None = None
    MINIO_SECRET_KEY: str | None = None
    MINIO_BUCKET_NAME: str | None = None
    MINIO_USE_SSL: bool = False
    MINIO_CDN_URL: str | None = None

    # Cache settings
    CACHE_TYPE: str = "memory"  # Options: memory, redis
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_PASSWORD: str | None = None
    REDIS_DB: int = 0
    REDIS_SSL: bool = False
    
    # Rate limiting settings
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS: int = 100  # Max requests allowed per window
    RATE_LIMIT_WINDOW_SECONDS: int = 1  # Window size (1 = per second, 60 = per minute)
    RATE_LIMIT_EXEMPT_PATHS: list[str] = ["/health", "/swagger", "/redoc", "/openapi.json"]  # Paths exempt from rate limiting
    
    # Seq logging settings
    SEQ_ENABLED: bool = False
    SEQ_SERVER_URL: str = "http://localhost:5341"
    SEQ_API_KEY: str = ""  # Optional: Seq API key for authentication

    model_config = SettingsConfigDict(
        env_file=f".env.{os.getenv('ENV', 'development')}",
        env_file_encoding="utf-8"
    )

    # OpenAPI / Swagger settings
    OPENAPI_TITLE: str = "Python FastAPI Boilerplate"
    OPENAPI_DESCRIPTION: str = (
        "A robust FastAPI boilerplate for rapid API development, featuring dependency "
        "injection, modular routing, and environment-based configuration."
    )
    OPENAPI_VERSION: str = "1.0.0"
    OPENAPI_ENABLED: bool = True

settings = Settings()
