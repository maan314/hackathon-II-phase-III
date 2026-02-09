"""
Database seed script for test data.

Creates sample tasks for testing purposes.
"""
from sqlmodel import Session
from backend.mcp.db.engine import engine
from backend.mcp.db.models import Task, TaskStatus
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def seed_database():
    """
    Seed database with test data.
    
    Creates 2 test users with 5 tasks each (mix of pending and completed).
    """
    test_users = ["user123", "user456"]
    
    with Session(engine) as session:
        for user_id in test_users:
            logger.info(f"Creating test tasks for {user_id}")
            
            # Create 5 tasks per user
            tasks = [
                Task(
                    user_id=user_id,
                    title=f"Review the proposal",
                    description="Review and provide feedback on the Q4 proposal",
                    status=TaskStatus.PENDING,
                    due_date=datetime.utcnow() + timedelta(days=7)
                ),
                Task(
                    user_id=user_id,
                    title=f"Update documentation",
                    description="Update API documentation with new endpoints",
                    status=TaskStatus.COMPLETED,
                    due_date=None
                ),
                Task(
                    user_id=user_id,
                    title=f"Fix bug in login flow",
                    description=None,
                    status=TaskStatus.PENDING,
                    due_date=datetime.utcnow() + timedelta(days=3)
                ),
                Task(
                    user_id=user_id,
                    title=f"Prepare presentation",
                    description="Prepare slides for team meeting",
                    status=TaskStatus.COMPLETED,
                    due_date=None
                ),
                Task(
                    user_id=user_id,
                    title=f"Code review",
                    description="Review pull requests from team members",
                    status=TaskStatus.PENDING,
                    due_date=datetime.utcnow() + timedelta(days=1)
                ),
            ]
            
            for task in tasks:
                session.add(task)
            
            session.commit()
            logger.info(f"✓ Created 5 tasks for {user_id}")
    
    logger.info("Database seeding completed successfully!")


if __name__ == "__main__":
    seed_database()
