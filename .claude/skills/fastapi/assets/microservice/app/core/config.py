"""Configuration settings."""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    project_name: str = "Product Microservice"
    api_v1_prefix: str = "/api/v1"

    # External services
    inventory_service_url: str = "http://localhost:8001"
    payment_service_url: str = "http://localhost:8002"

    # CORS
    allowed_origins: list[str] = ["*"]

    # Redis cache (optional)
    redis_url: str = "redis://localhost:6379"
    cache_ttl: int = 300  # 5 minutes

    class Config:
        env_file = ".env"


settings = Settings()
