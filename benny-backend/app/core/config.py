"""
Application configuration - Simplified version.
"""
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Application
    app_name: str = "Benny Wellness AI"
    debug: bool = False
    secret_key: str = "dev-secret-key-change-in-production"
    
    # Database
    database_url: str = "postgresql+asyncpg://localhost:5432/wellness_dev"
    database_pool_size: int = 10
    database_max_overflow: int = 20
    
    # CORS - Simple approach
    frontend_url: str = "http://localhost:5173"
    cors_allow_credentials: bool = True
    
    # External Services
    ai_service_url: str = "http://127.0.0.1:8001"
    
    # Server
    host: str = "127.0.0.1"
    port: int = 8000
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra='ignore'
    )
    
    @property
    def allowed_origins(self) -> List[str]:
        """
        Get allowed CORS origins.
        Returns default dev origins since we don't need dynamic config yet.
        """
        return [
            self.frontend_url,  # Use configured frontend URL
            "http://localhost:5173",
            "http://localhost:3000",
            "http://127.0.0.1:5173",
            "http://127.0.0.1:3000"
        ]


settings = Settings()