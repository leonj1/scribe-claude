from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # Google OAuth (optional for boot)
    GOOGLE_CLIENT_ID: Optional[str] = ""
    GOOGLE_CLIENT_SECRET: Optional[str] = ""
    REDIRECT_URI: Optional[str] = "http://localhost:8000/auth/google/callback"

    # JWT
    JWT_SECRET: str = os.getenv("JWT_SECRET", "dev-insecure-change-me")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 10080  # 7 days

    # Database (default to SQLite so the app can boot without MySQL)
    MYSQL_URL: str = os.getenv("MYSQL_URL", "sqlite:///./app.db")

    # LLM Provider (optional for boot)
    LLM_API_KEY: Optional[str] = ""

    # Storage
    AUDIO_STORAGE_PATH: str = os.getenv("AUDIO_STORAGE_PATH", "/app/audio_storage")

    # Encryption (must be a valid Fernet key; provide a safe dev default)
    # NOTE: Replace in production via env var.
    ENCRYPTION_KEY: str = os.getenv(
        "ENCRYPTION_KEY",
        # Pre-generated Fernet key for development only
        "y1m8S2q7ZyX0zKcN3b7LZc5qk0cD8mJ3sHkC3n0l6cE="
    )

    # Frontend
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
