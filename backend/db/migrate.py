"""
Database migration runner for AI Chat Agent system.

Executes SQL migration scripts in order.
"""

import psycopg2
from pathlib import Path
import logging
from backend.config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_migrations():
    """
    Run all SQL migration scripts in order.

    Connects to Neon PostgreSQL and executes migration files.
    """
    migrations_dir = Path(__file__).parent / "migrations"
    migration_files = sorted(migrations_dir.glob("*.sql"))

    if not migration_files:
        logger.warning("No migration files found")
        return

    logger.info(f"Found {len(migration_files)} migration files")

    # Connect to database
    try:
        conn = psycopg2.connect(Config.DATABASE_URL)
        conn.autocommit = True
        cursor = conn.cursor()

        logger.info("Connected to database")

        # Execute each migration
        for migration_file in migration_files:
            logger.info(f"Running migration: {migration_file.name}")

            with open(migration_file, 'r') as f:
                sql = f.read()

            try:
                cursor.execute(sql)
                logger.info(f"✓ Migration {migration_file.name} completed")
            except Exception as e:
                logger.error(f"✗ Migration {migration_file.name} failed: {e}")
                raise

        cursor.close()
        conn.close()

        logger.info("All migrations completed successfully")

    except Exception as e:
        logger.error(f"Migration failed: {e}")
        raise


if __name__ == "__main__":
    run_migrations()
