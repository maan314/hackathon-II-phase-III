"""Script to initialize the database tables."""
from database import engine
from models import User, Todo  # Import models to register them
from sqlmodel import SQLModel

def create_tables():
    """Create all tables in the database."""
    print("Creating database tables...")
    SQLModel.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

if __name__ == "__main__":
    create_tables()