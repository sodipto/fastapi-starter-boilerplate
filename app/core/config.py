
import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ENV: str
    DATABASE_URL: str

    class Config:
        env_file = f".env.{os.getenv('ENV', 'development')}"


settings = Settings()
