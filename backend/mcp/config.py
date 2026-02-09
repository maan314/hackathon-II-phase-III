"""
Configuration management for MCP server.

Loads environment variables and provides configuration settings.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Configuration settings for MCP server."""
    
    # Database Configuration
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    
    # MCP Server Configuration
    MCP_SERVER_PORT: int = int(os.getenv("MCP_SERVER_PORT", "8001"))
    MCP_SERVER_HOST: str = os.getenv("MCP_SERVER_HOST", "0.0.0.0")
    
    # Application Configuration
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    @classmethod
    def validate(cls):
        """Validate required configuration settings."""
        if not cls.DATABASE_URL:
            raise ValueError("DATABASE_URL environment variable is required")
        
        if not cls.DATABASE_URL.startswith("postgresql://"):
            raise ValueError("DATABASE_URL must be a PostgreSQL connection string")


# Create global config instance
config = Config()
