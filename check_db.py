import sys
import os

# Add backend directory to Python path
backend_dir = os.path.join(os.getcwd(), 'backend')
sys.path.insert(0, backend_dir)

from backend.database import engine
from backend.models.user import User
from sqlmodel import select, Session

# Query the database using the same engine as the application
with Session(engine) as session:
    statement = select(User)
    users = session.exec(statement).all()
    
    print(f"Found {len(users)} users in the database:")
    for user in users:
        print(f"ID: {user.id}, Email: {user.email}, Name: {user.first_name} {user.last_name}")