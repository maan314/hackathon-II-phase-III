"""
Database connection management for AI Chat Agent system.

Provides connection pooling for Neon PostgreSQL with stateless design.
No in-memory session state - each request gets a fresh session from the pool.
"""

from sqlmodel import create_engine, Session
from contextlib import contextmanager
from typing import Generator
import logging

from backend.config import Config

logger = logging.getLogger(__name__)


# Create SQLModel engine with connection pooling
# Stateless Design: Connection pool provides fresh connections per request
# No session state maintained between requests
engine = create_engine(
    Config.DATABASE_URL,
    pool_size=Config.DB_POOL_SIZE,          # Number of persistent connections
    max_overflow=Config.DB_MAX_OVERFLOW,    # Additional connections when pool exhausted
    pool_timeout=Config.DB_POOL_TIMEOUT,    # Wait time for connection (seconds)
    pool_recycle=Config.DB_POOL_RECYCLE,    # Recycle connections after N seconds
    pool_pre_ping=True,                      # Verify connections before use
    echo=Config.is_development(),            # Log SQL in development
)


@contextmanager
def get_session() -> Generator[Session, None, None]:
    """
    Context manager for database sessions.

    Stateless Design:
    - Creates fresh session from connection pool
    - No session state persists between requests
    - Automatic cleanup on context exit

    Usage:
        with get_session() as session:
            conversation = session.query(Conversation).filter(...).first()

    Yields:
        Session: SQLModel database session

    Raises:
        Exception: Database connection or query errors
    """
    session = Session(engine)
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Database error: {e}")
        raise
    finally:
        session.close()


def init_db():
    """
    Initialize database by creating all tables.

    This is typically called during application startup.
    For production, use migration scripts instead.
    """
    from backend.db.models import Conversation, Message

    try:
        # Import all models to ensure they're registered
        # Create all tables
        from sqlmodel import SQLModel
        SQLModel.metadata.create_all(engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


def test_connection() -> bool:
    """
    Test database connection.

    Returns:
        bool: True if connection successful, False otherwise
    """
    try:
        with get_session() as session:
            # Execute simple query to test connection
            session.execute("SELECT 1")
        logger.info("Database connection test successful")
        return True
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        return False
