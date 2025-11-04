from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Google OAuth
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    REDIRECT_URI: str

    # JWT
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 10080  # 7 days

    # Database
    MYSQL_URL: str

    # LLM Provider
    LLM_API_KEY: str

    # Storage
    AUDIO_STORAGE_PATH: str

    # Encryption
    ENCRYPTION_KEY: str

    # Frontend
    FRONTEND_URL: str = "http://localhost:3000"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
