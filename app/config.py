from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    # Railway provides DATABASE_URL, fallback to SQLite for local
    database_url: str = "sqlite:///./data/botbuilder.db"

    # Redis
    redis_url: str = "redis://localhost:6379"
    use_redis: bool = False

    # Security
    secret_key: str = "your-secret-key-change-this-in-production"
    admin_password: str = "changeme"

    # API
    api_base_url: str = "http://localhost:8000"
    frontend_url: str = "http://localhost:3000"
    allowed_origins: str = "http://localhost:3000,http://localhost:8000"

    # Default API Keys (optional)
    default_anthropic_api_key: Optional[str] = None
    default_openai_api_key: Optional[str] = None

    # Qdrant
    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: Optional[str] = None

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
