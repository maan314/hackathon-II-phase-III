"""
Database migration runner.

Executes SQL migration scripts to set up database schema.
"""
import os
from pathlib import Path
from sqlmodel import Session, text
from backend.mcp.db.engine import engine
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_migrations():
    """
    Execute all SQL migration scripts in order.
    
    Migrations are executed from the migrations/ directory in numerical order.
    """
    migrations_dir = Path(__file__).parent / "migrations"
    
    if not migrations_dir.exists():
        logger.error(f"Migrations directory not found: {migrations_dir}")
        return False
    
    # Get all .sql files sorted by name
    migration_files = sorted(migrations_dir.glob("*.sql"))
    
    if not migration_files:
        logger.warning("No migration files found")
        return True
    
    logger.info(f"Found {len(migration_files)} migration(s)")
    
    with Session(engine) as session:
        for migration_file in migration_files:
            logger.info(f"Running migration: {migration_file.name}")
            
            try:
                # Read migration SQL
                sql_content = migration_file.read_text()
                
                # Execute migration
                session.exec(text(sql_content))
                session.commit()
                
                logger.info(f"✓ Migration {migration_file.name} completed successfully")
                
            except Exception as e:
                logger.error(f"✗ Migration {migration_file.name} failed: {str(e)}")
                session.rollback()
                return False
    
    logger.info("All migrations completed successfully!")
    return True


if __name__ == "__main__":
    success = run_migrations()
    exit(0 if success else 1)
