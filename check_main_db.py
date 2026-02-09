import os
from sqlmodel import create_engine, Session, select
from backend.models.user import User

# Create engine pointing to the main directory database
current_dir = os.getcwd()
db_path = os.path.join(current_dir, "todo_app_local.db")
database_url = f"sqlite:///{db_path}"

print(f"Connecting to database: {database_url}")

engine = create_engine(database_url)

with Session(engine) as session:
    statement = select(User)
    users = session.exec(statement).all()
    
    print(f"Found {len(users)} users in the database:")
    for user in users:
        print(f"ID: {user.id}, Email: {user.email}, Name: {user.first_name} {user.last_name}")