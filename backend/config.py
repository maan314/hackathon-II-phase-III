"""
Configuration module for AI Chat Agent system.

Loads environment variables and provides configuration settings.
All sensitive data (database URLs, API keys) loaded from environment.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """
    Application configuration loaded from environment variables.

    Required Environment Variables:
    - DATABASE_URL: Neon PostgreSQL connection string
    - OPENAI_API_KEY: OpenAI API key for agent processing

    Optional Environment Variables:
    - ENVIRONMENT: development/production (default: development)
    - LOG_LEVEL: INFO/DEBUG/WARNING/ERROR (default: INFO)
    """

    # Database Configuration
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")

    # OpenAI Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

    # Application Configuration
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # Database Connection Pool Settings
    DB_POOL_SIZE: int = int(os.getenv("DB_POOL_SIZE", "10"))
    DB_MAX_OVERFLOW: int = int(os.getenv("DB_MAX_OVERFLOW", "20"))
    DB_POOL_TIMEOUT: int = int(os.getenv("DB_POOL_TIMEOUT", "30"))
    DB_POOL_RECYCLE: int = int(os.getenv("DB_POOL_RECYCLE", "3600"))

    # API Configuration
    API_TIMEOUT: int = int(os.getenv("API_TIMEOUT", "10"))

    @classmethod
    def validate(cls):
        """
        Validate that required configuration is present.

        Raises:
            ValueError: If required environment variables are missing
        """
        if not cls.DATABASE_URL:
            raise ValueError("DATABASE_URL environment variable is required")

        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY environment variable is required")

    @classmethod
    def is_production(cls) -> bool:
        """Check if running in production environment."""
        return cls.ENVIRONMENT.lower() == "production"

    @classmethod
    def is_development(cls) -> bool:
        """Check if running in development environment."""
        return cls.ENVIRONMENT.lower() == "development"


# Validate configuration on module load
Config.validate()
