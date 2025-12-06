"""
Configuration settings for Safety Event Classification API

Environment-based configuration following best practices.
"""

import os
from typing import List
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings with environment variable support"""

    # Application
    APP_NAME: str = "Safety Event Classification API"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    PORT: int = int(os.getenv("PORT", "9000"))

    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:5000",
        "http://localhost:8080",
    ]

    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24

    # Google Cloud
    GCP_PROJECT: str = os.getenv("GCP_PROJECT", "")
    GCP_REGION: str = os.getenv("GCP_REGION", "us-central1")
    GOOGLE_APPLICATION_CREDENTIALS: str = os.getenv(
        "GOOGLE_APPLICATION_CREDENTIALS", "/secrets/llm-service-account.json"
    )

    # LLM Configuration
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gemini-2.0-flash-exp")
    LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.2"))
    LLM_MAX_TOKENS: int = int(os.getenv("LLM_MAX_TOKENS", "1000"))

    # Audio Service
    AUDIO_MAX_FILE_SIZE_MB: int = 50
    SUPPORTED_AUDIO_FORMATS: List[str] = ["mp3", "wav", "m4a", "flac", "ogg"]
    SUPPORTED_LANGUAGES: List[str] = ["en-US", "zh-CN", "zh-HK", "fr-FR", "es-ES"]

    # File Upload
    UPLOAD_FOLDER: str = "/tmp/uploads"
    MAX_UPLOAD_SIZE_MB: int = 25

    # Departments
    VALID_DEPARTMENTS: List[str] = ["internal medicine", "surgery", "ob/gyn/nicu", "radiology/imaging", "outpatient/ER"]

    class Config:
        """Pydantic config"""

        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Global settings instance
settings = get_settings()
