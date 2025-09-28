"""
Application configuration using Pydantic Settings.
Handles environment variables with type validation.
"""
from typing import List, Optional
from pydantic import BaseSettings, validator
import os


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    # Application
    app_name: str = "Benny Wellness AI"
    debug: bool = False
    secret_key: str

    # Database
    database_url: str
    database_pool_size: int = 10
    database_max_overflow: int = 20

    # CORS
    frontend_url: str = "http://localhost:5173"
    allowed_origins: List[str] = []

    # External Services
    ai_service_url: str = "http://127.0.0.1:8001"
    azure_open_ai_endpoint: Optional[str] = None
    azure_open_api_key: Optional[str] = None

    # Server
    host: str = "127.0.0.1"
    port: int = 8000

    @validator('allowed_origines', pre=True)
    def parse_cors_origines(cls, v):
        """Parse CORS origins from environment variable."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',')]
        return v or [
            "http://localhost:5173",
            "http://localhost:3000",
            "http://127.0.0.1:5173",
            "http://127.0.0.1:3000"
        ]

    @validator('database_url')
    def validate_database_url(cls, v):
        """Ensure database URL is provided."""
        if not v:
            raise ValueError('DATABASE_URL environment variable is required')
        return v

    class Config():
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
