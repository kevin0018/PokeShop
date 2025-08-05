"""Application configuration settings."""

from functools import lru_cache
from typing import List
from pydantic import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    environment: str = "development"
    
    # Database settings
    database_url: str
    database_test_url: str
    
    # Redis settings
    redis_url: str = "redis://localhost:6379/0"
    
    # JWT settings
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    
    # CORS settings
    allowed_origins: List[str] = ["http://localhost:5173"]
    
    # External APIs
    pokeapi_base_url: str = "https://pokeapi.co/api/v2"
    openai_api_key: str = ""
    stripe_secret_key: str = ""
    stripe_publishable_key: str = ""
    
    # Cloudinary settings
    cloudinary_cloud_name: str = ""
    cloudinary_api_key: str = ""
    cloudinary_api_secret: str = ""
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()
