# Quickstart Guide: Todo Web Application Authentication Layer

## Prerequisites

- Python 3.9 or higher
- FastAPI backend from the previous feature (1-todo-backend-api)
- Access to environment variables for secret configuration
- Understanding of JWT concepts

## Setup Instructions

### 1. Install Dependencies
Add the following to your requirements.txt or install directly:
```bash
pip install python-jose[cryptography] passlib[bcrypt] python-multipart
```

### 2. Environment Configuration
Update your `.env` file with the following variables:
```bash
# JWT Configuration
SECRET_KEY="your-super-secret-key-here-make-it-long-and-random"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

### 3. Project Structure
Add the following files to your existing project structure:
```
todo-backend-api/
├── auth/
│   ├── __init__.py
│   ├── jwt_handler.py          # JWT utility functions
│   └── jwt_bearer.py         # Custom JWT Bearer authentication
├── main.py                   # Updated with authentication
├── models.py                 # Updated models
├── database.py
├── crud.py                   # Updated with user isolation
├── schemas.py                # Updated schemas
├── config.py                 # Updated configuration
└── requirements.txt
```

## Implementation

### auth/jwt_handler.py - JWT Utility Functions
```python
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt

def verify_token(token: str):
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        user_id: int = payload.get("sub")
        if user_id is None:
            return None
        return user_id
    except JWTError:
        return None
```

### auth/jwt_bearer.py - JWT Bearer Authentication
```python
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from auth.jwt_handler import verify_token

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    user_id = verify_token(token)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user_id
```

### config.py - Updated Configuration
```python
from functools import lru_cache
from sqlmodel import Session
from pydantic_settings import BaseSettings
from database import engine

class Settings(BaseSettings):
    database_url: str
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()

def get_session():
    with Session(engine) as session:
        yield session
```

### Update existing models.py to include authentication considerations
```python
# In your existing models.py file, ensure the Task model enforces user_id foreign key
# The existing model should already support user_id as foreign key for isolation
```

### Update main.py with authentication
```python
from fastapi import FastAPI, Depends
from auth.jwt_bearer import get_current_user
from models import Task
from typing import List
from config import get_session
from sqlmodel import Session

app = FastAPI(title="Todo Backend API with Authentication", version="1.0.0")

@app.post("/api/v1/tasks", response_model=Task, status_code=201)
def create_new_task(
    task: TaskCreate,
    current_user_id: int = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # Set the user_id to the authenticated user
    task_data = task.dict()
    task_data['user_id'] = current_user_id
    db_task = Task(**task_data)
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task

@app.get("/api/v1/tasks", response_model=List[Task])
def read_tasks(
    current_user_id: int = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # Only return tasks belonging to the authenticated user
    tasks = session.query(Task).filter(Task.user_id == current_user_id).all()
    return tasks

@app.get("/api/v1/tasks/{task_id}", response_model=Task)
def read_task(
    task_id: int,
    current_user_id: int = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # Only allow access to tasks belonging to the authenticated user
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.user_id != current_user_id:
        raise HTTPException(status_code=403, detail="Access denied: insufficient permissions")
    return task

@app.put("/api/v1/tasks/{task_id}", response_model=Task)
def update_existing_task(
    task_id: int,
    task_update: TaskUpdate,
    current_user_id: int = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # Only allow updates to tasks belonging to the authenticated user
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.user_id != current_user_id:
        raise HTTPException(status_code=403, detail="Access denied: insufficient permissions")

    update_data = task_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)

    session.add(task)
    session.commit()
    session.refresh(task)
    return task

@app.delete("/api/v1/tasks/{task_id}", status_code=204)
def delete_existing_task(
    task_id: int,
    current_user_id: int = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # Only allow deletion of tasks belonging to the authenticated user
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.user_id != current_user_id:
        raise HTTPException(status_code=403, detail="Access denied: insufficient permissions")

    session.delete(task)
    session.commit()
    return
```

## Testing the Authentication

### Test Authentication Flows

1. **Requests without token → 401**
```bash
curl -X GET "http://localhost:8000/api/v1/tasks"
# Response: 401 {"detail": "Could not validate credentials"}
```

2. **Requests with invalid token → 401**
```bash
curl -X GET "http://localhost:8000/api/v1/tasks" \
  -H "Authorization: Bearer invalid.token.here"
# Response: 401 {"detail": "Could not validate credentials"}
```

3. **Requests with mismatched user_id → 403/404**
```bash
curl -X GET "http://localhost:8000/api/v1/tasks/999" \
  -H "Authorization: Bearer valid_token_for_user_1"
# If task belongs to user 2: Response: 403 {"detail": "Access denied: insufficient permissions"}
```

4. **Requests with valid token → succeed**
```bash
curl -X GET "http://localhost:8000/api/v1/tasks" \
  -H "Authorization: Bearer valid_token_for_user_1"
# Response: 200 [tasks belonging to user 1]
```

## Next Steps

1. Integrate with a frontend authentication system that generates JWT tokens
2. Implement proper user management for token generation
3. Add refresh token functionality if needed
4. Set up proper logging for authentication events
5. Implement rate limiting for authentication attempts