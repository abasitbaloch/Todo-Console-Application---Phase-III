"""Application configuration from environment variables."""

import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # --- Database ---
    # Defaulting to /tmp/ ensures we have write access on Hugging Face
    DATABASE_URL: str = "sqlite:////tmp/todo.db"

    # --- JWT Configuration ---
    # Providing a default prevents a 500 error if the secret is missing
    JWT_SECRET: str = "super-secret-key-change-this-later"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24

    # --- CORS Configuration ---
    CORS_ORIGINS: str = "*"

    # --- Environment ---
    ENVIRONMENT: str = "production"

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS_ORIGINS into a list."""
        if self.CORS_ORIGINS == "*":
            return ["*"]
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    # Updated for Pydantic V2
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"
    )

settings = Settings()