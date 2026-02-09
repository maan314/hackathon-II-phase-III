"""
Database engine configuration with connection pooling.

Provides SQLModel engine for database operations.
"""
from sqlmodel import create_engine
from backend.mcp.config import config


# Create database engine with connection pooling
engine = create_engine(
    config.DATABASE_URL,
    echo=config.ENVIRONMENT == "development",  # Log SQL queries in development
    pool_size=10,  # Number of persistent connections
    max_overflow=20,  # Additional connections when pool exhausted
    pool_timeout=30,  # Wait time for connection (seconds)
    pool_recycle=3600,  # Recycle connections after 1 hour
    pool_pre_ping=True,  # Verify connections before using
)


def get_engine():
    """Get database engine instance."""
    return engine
