import sys
import os

# Add backend directory to Python path
backend_dir = os.path.join(os.getcwd(), 'backend')
sys.path.insert(0, backend_dir)

from backend.database import engine
from backend.models.user import User, UserCreate
from backend.services.auth_service import create_user
from sqlmodel import Session

# Test creating a user directly using the same service as the API
user_data = UserCreate(
    email="direct_test@example.com",
    password="TestPass123",
    first_name="Direct",
    last_name="Test"
)

with Session(engine) as session:
    try:
        print("Attempting to create user directly...")
        new_user = create_user(session=session, user_create=user_data)
        print(f"User created successfully: ID {new_user.id}, Email: {new_user.email}")
        
        # Query to verify the user exists
        from sqlmodel import select
        statement = select(User)
        users = session.exec(statement).all()
        print(f"Total users in database after creation: {len(users)}")
        
        # Print the last user
        if users:
            last_user = users[-1]
            print(f"Last user: ID {last_user.id}, Email: {last_user.email}")
        
    except Exception as e:
        print(f"Error creating user: {e}")
        import traceback
        traceback.print_exc()