from dotenv import load_dotenv
from sqlmodel import create_engine, Session
import os
import urllib.parse

load_dotenv()

# Use environment variable for database URL, fallback to SQLite for local development
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./todo_app_local.db")

# If using SQLite with relative path, convert to absolute path to ensure consistent location
if DATABASE_URL.startswith("sqlite:///./"):
    # Get the directory of this file (backend directory) and build absolute path
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    db_relative_path = DATABASE_URL[len("sqlite:///."):]
    db_absolute_path = os.path.abspath(os.path.join(backend_dir, db_relative_path))
    DATABASE_URL = f"sqlite:///{db_absolute_path}"

# Create the database engine
# For PostgreSQL, we don't need special connect_args, but for SQLite we do
if DATABASE_URL.startswith("postgresql"):
    # For Neon PostgreSQL, we may need to handle special parameters
    # Parse the URL to potentially remove problematic parameters
    parsed_url = urllib.parse.urlparse(DATABASE_URL)
    if 'channel_binding' in parsed_url.query:
        # Remove channel_binding parameter which can cause issues with some clients
        query_params = urllib.parse.parse_qs(parsed_url.query)
        query_params.pop('channel_binding', None)
        new_query = urllib.parse.urlencode(query_params, doseq=True)
        DATABASE_URL = urllib.parse.urlunparse((
            parsed_url.scheme, parsed_url.netloc, parsed_url.path,
            parsed_url.params, new_query, parsed_url.fragment
        ))
    
    # PostgreSQL connection with connection pooling and retry logic
    engine = create_engine(
        DATABASE_URL,
        echo=True,
        pool_pre_ping=True,  # Test connections before using them
        pool_size=5,  # Number of connections to maintain
        max_overflow=10,  # Additional connections when pool is full
        pool_recycle=3600,  # Recycle connections after 1 hour
        connect_args={
            "connect_timeout": 10,  # Connection timeout in seconds
            "keepalives": 1,
            "keepalives_idle": 30,
            "keepalives_interval": 10,
            "keepalives_count": 5,
        }
    )
else:
    # SQLite connection
    connect_args = {"check_same_thread": False}
    engine = create_engine(DATABASE_URL, echo=True, connect_args=connect_args)

def get_session():
    with Session(engine) as session:
        yield session
