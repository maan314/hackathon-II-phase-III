import os
import sys

# Add backend directory to Python path
backend_dir = os.path.join(os.getcwd(), 'backend')
sys.path.insert(0, backend_dir)

from sqlmodel import create_engine, Session, select
from backend.models.user import User

# Create engine with the same path logic as the updated database.py
db_relative_path = "./todo_app_local.db"
db_absolute_path = os.path.abspath(os.path.join(backend_dir, db_relative_path))
DATABASE_URL = f"sqlite:///{db_absolute_path}"

print(f"Connecting to database: {DATABASE_URL}")

engine = create_engine(DATABASE_URL)

with Session(engine) as session:
    statement = select(User)
    users = session.exec(statement).all()
    
    print(f"Found {len(users)} users in the database:")
    for user in users:
        print(f"ID: {user.id}, Email: {user.email}, Name: {user.first_name} {user.last_name}")