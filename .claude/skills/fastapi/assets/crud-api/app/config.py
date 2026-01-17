"""
Configuration settings for the application.
"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # Database
    database_url: str = "postgresql+asyncpg://user:password@localhost:5432/dbname"

    # API
    api_v1_prefix: str = "/api/v1"
    project_name: str = "FastAPI CRUD API"

    # Security
    secret_key: str = "your-secret-key-change-this"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    class Config:
        env_file = ".env"


settings = Settings()
