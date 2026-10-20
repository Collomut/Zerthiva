"""
Application Settings & Environment Configuration
"""

from typing import List, Union
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import AnyHttpUrl, validator


class Settings(BaseSettings):
    PROJECT_NAME: str = "Zerthiva Cloud Platform"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Security
    SECRET_KEY: str = "zerthiva-super-secret-key-change-in-production-min-32-chars"
    DEVICE_PSK: str = "sg-field-device-pre-shared-key-2026"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    ALGORITHM: str = "HS256"

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "*"
    ]

    # Database
    # Default to async SQLite for local zero-dependency testing; can be overridden by environment variable
    DATABASE_URL: str = "sqlite+aiosqlite:///./zerthiva.db"

    # SMS Gateway Configuration
    SMS_PROVIDER: str = "mock" # "mock", "africastalking", "twilio"
    AFRICASTALKING_USERNAME: str = "sandbox"
    AFRICASTALKING_API_KEY: str = ""
    AFRICASTALKING_SENDER_ID: str = "Zerthiva"

    # Agronomic Thresholds
    DEFAULT_IRRIGATION_WATER_EC: float = 0.6
    MIN_LEACHING_REQUIREMENT: float = 0.05
    MAX_LEACHING_REQUIREMENT: float = 0.45

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()
