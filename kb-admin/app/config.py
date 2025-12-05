"""
Configuration management for KB-Admin service
"""
import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Service configuration
    SERVICE_NAME: str = "kb-admin"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True

    # Redis configuration
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://redis:6379")
    REDIS_DB: int = 0

    # MySQL configuration
    DB_HOST: str = os.getenv("DB_HOST", "mysql")
    DB_PORT: int = int(os.getenv("DB_PORT", "3306"))
    DB_USERNAME: str = os.getenv("DB_USERNAME", "root")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "root")
    DB_DATABASE: str = os.getenv("DB_DATABASE", "laravel")

    # External services
    LARAVEL_API_URL: str = os.getenv("LARAVEL_API_URL", "http://laravel-app-dev:8000")
    IDEA_AGENT_URL: str = os.getenv("IDEA_AGENT_URL", "http://idea-agent:8000")

    # Embedding configuration
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
    DEFAULT_EMBEDDING_PROVIDER: str = "openai"
    DEFAULT_EMBEDDING_MODEL: str = "text-embedding-3-small"

    # Chunking configuration
    DEFAULT_CHUNK_SIZE: int = 1000
    DEFAULT_CHUNK_OVERLAP: int = 200
    MAX_CHUNK_SIZE: int = 2000

    # File upload configuration
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: set = {".md", ".txt", ".pdf"}
    UPLOAD_DIR: str = "./uploads"

    # Vector search configuration
    DEFAULT_SEARCH_K: int = 3
    MAX_SEARCH_K: int = 10

    # Self-learning configuration
    MIN_QA_LENGTH: int = 100
    MIN_CONFIDENCE_SCORE: float = 0.7
    AUTO_APPROVE_THRESHOLD: float = 0.95  # Future: auto-approve high confidence

    # Rate limiting
    EMBEDDING_BATCH_SIZE: int = 50
    EMBEDDING_RATE_LIMIT_PER_MIN: int = 100

    class Config:
        env_file = ".env"
        case_sensitive = True


# Singleton settings instance
settings = Settings()
