import os
import sys

# Add backend to path
backend_path = os.path.join(os.getcwd(), 'backend')
sys.path.insert(0, backend_path)

# Import and check the database configuration
from backend.database import DATABASE_URL, engine
print(f"Current working directory: {os.getcwd()}")
print(f"Backend directory: {backend_path}")
print(f"Database URL: {DATABASE_URL}")

# Check if it's a SQLite database and the file path
if DATABASE_URL.startswith('sqlite:///'):
    db_path = DATABASE_URL.replace('sqlite:///', '')
    print(f"SQLite file path (relative): {db_path}")
    
    # Convert to absolute path
    abs_path = os.path.abspath(db_path)
    print(f"SQLite file path (absolute): {abs_path}")
    
    # Check if file exists
    if os.path.exists(abs_path):
        print(f"Database file exists: Yes")
        print(f"Database file size: {os.path.getsize(abs_path)} bytes")
    else:
        print(f"Database file exists: No")