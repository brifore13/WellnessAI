"""
AI Service Configuration
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """AI service configuration with environment variable support."""

    # Azure OpenAI
    azure_openai_endpoint: str
    azure_openai_api_key: str
    azure_openai_deployment: str = "gpt-35-turbo"
    azure_openai_api_version: str = "2025-preview"

    # CORS
    frontend_url: str = "http://localhost:5173"
    backend_url: str = "http://localhost:8000"

    # Server
    host: str = "127.0.0.1"
    port: int = 8001

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False
    )


settings = Settings()