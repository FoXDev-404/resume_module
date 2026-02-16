"""
Configuration management for Resume Optimization SaaS.
Handles environment variables, API keys, and application settings.
"""

import os
from pydantic_settings import BaseSettings
from pydantic import field_validator
import google.generativeai as genai


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Gemini API Configuration
    GEMINI_API_KEY: str
    GEMINI_EMBEDDING_MODEL: str = "models/embedding-001"
    GEMINI_TEXT_MODEL: str = "gemini-1.5-flash"

    # Application Configuration
    MAX_RESUME_SIZE_MB: int = 5
    ALLOWED_FILE_TYPES: str = ".pdf,.txt"
    MAX_JD_LENGTH: int = 50000
    MIN_JD_LENGTH: int = 50

    # Environment
    ENV: str = "development"

    # Keyword Extraction
    TOP_KEYWORDS_COUNT: int = 30

    # Bullet Rewrite Configuration
    MAX_BULLETS_TO_REWRITE: int = 3
    MAX_KEYWORDS_TO_INJECT: int = 5

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

    @field_validator('GEMINI_API_KEY')
    @classmethod
    def validate_api_key(cls, v: str) -> str:
        """Validate that API key is properly configured."""
        if not v or v == "your_api_key_here":
            raise ValueError(
                "GEMINI_API_KEY not configured. Please set it in .env file"
            )
        return v

    @field_validator('MAX_RESUME_SIZE_MB')
    @classmethod
    def validate_max_size(cls, v: int) -> int:
        """Ensure max file size is reasonable."""
        if v < 1 or v > 20:
            raise ValueError("MAX_RESUME_SIZE_MB must be between 1 and 20")
        return v

    def max_resume_size_bytes(self) -> int:
        """Get max resume size in bytes."""
        return self.MAX_RESUME_SIZE_MB * 1024 * 1024

    def get_allowed_file_types(self) -> list:
        """Get list of allowed file types."""
        return [ft.strip() for ft in self.ALLOWED_FILE_TYPES.split(',')]


# Initialize settings
settings = Settings()

# Configure Gemini API (done once at module level)
genai.configure(api_key=settings.GEMINI_API_KEY)


def get_settings() -> Settings:
    """Get application settings instance."""
    return settings
