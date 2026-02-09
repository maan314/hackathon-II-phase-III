# Quickstart Guide: Todo Web Application Backend API

## Prerequisites

- Python 3.9 or higher
- pip package manager
- Access to a PostgreSQL database (Neon Serverless recommended)
- Environment where you can set environment variables

## Setup Instructions

### 1. Clone or Create Project Directory
```bash
mkdir todo-backend-api
cd todo-backend-api
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install fastapi sqlmodel uvicorn psycopg2-binary python-jose[cryptography] passlib[bcrypt]
```

### 4. Environment Configuration
Create a `.env` file with the following variables:
```bash
DATABASE_URL="postgresql://username:password@host:port/database_name"
SECRET_KEY="your-secret-key-here"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

For Neon Serverless PostgreSQL, your DATABASE_URL would look like:
```
DATABASE_URL="postgresql://username:password@ep-xxx.us-east-1.aws.neon.tech/dbname?sslmode=require"
```

### 5. Project Structure
Create the following directory structure:
```
todo-backend-api/
├── main.py
├── models.py
├── database.py
├── crud.py
├── schemas.py
├── config.py
└── requirements.txt
```

## Basic Implementation

### main.py - FastAPI Application
```python
from fastapi import FastAPI, Depends, HTTPException
from typing import List
from sqlmodel import Session
from database import engine
from models import Task, TaskCreate, TaskUpdate
from crud import (
    create_task,
    get_task,
    get_tasks,
    update_task,
    delete_task
)
from config import get_session

app = FastAPI(title="Todo Backend API", version="1.0.0")

@app.on_event("startup")
def on_startup():
    from sqlmodel import SQLModel
    SQLModel.metadata.create_all(engine)

@app.post("/api/v1/tasks", response_model=Task, status_code=201)
def create_new_task(task: TaskCreate, session: Session = Depends(get_session)):
    return create_task(session, task)

@app.get("/api/v1/tasks", response_model=List[Task])
def read_tasks(session: Session = Depends(get_session)):
    return get_tasks(session)

@app.get("/api/v1/tasks/{task_id}", response_model=Task)
def read_task(task_id: int, session: Session = Depends(get_session)):
    task = get_task(session, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.put("/api/v1/tasks/{task_id}", response_model=Task)
def update_existing_task(
    task_id: int,
    task_update: TaskUpdate,
    session: Session = Depends(get_session)
):
    updated_task = update_task(session, task_id, task_update)
    if not updated_task:
        raise HTTPException(status_code=404, detail="Task not found")
    return updated_task

@app.delete("/api/v1/tasks/{task_id}", status_code=204)
def delete_existing_task(task_id: int, session: Session = Depends(get_session)):
    success = delete_task(session, task_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    return
```

### models.py - SQLModel Definitions
```python
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional
import enum

class TaskStatus(str, enum.Enum):
    pending = "pending"
    completed = "completed"

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

class TaskBase(SQLModel):
    title: str = Field(min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, max_length=1000)
    status: TaskStatus = Field(default=TaskStatus.pending)
    user_id: int = Field(foreign_key="user.id")

class Task(TaskBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

class TaskCreate(TaskBase):
    pass

class TaskUpdate(SQLModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, max_length=1000)
    status: Optional[TaskStatus] = None
```

### database.py - Database Connection
```python
from sqlalchemy import create_engine
from sqlmodel import SQLModel
from config import settings

engine = create_engine(settings.database_url)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
```

### config.py - Configuration Management
```python
from functools import lru_cache
from sqlmodel import Session
from pydantic_settings import BaseSettings
from database import engine

class Settings(BaseSettings):
    database_url: str
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

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

## Running the Application

### Start the Development Server
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`.

API documentation will be available at:
- `http://localhost:8000/docs` (Swagger UI)
- `http://localhost:8000/redoc` (ReDoc)

## Testing the API

Once the server is running, you can test the endpoints:

### Create a Task
```bash
curl -X POST "http://localhost:8000/api/v1/tasks" \
  -H "Content-Type: application/json" \
  -d '{"title": "Sample Task", "description": "This is a sample task"}'
```

### Get All Tasks
```bash
curl -X GET "http://localhost:8000/api/v1/tasks"
```

### Get a Specific Task
```bash
curl -X GET "http://localhost:8000/api/v1/tasks/1"
```

### Update a Task
```bash
curl -X PUT "http://localhost:8000/api/v1/tasks/1" \
  -H "Content-Type: application/json" \
  -d '{"title": "Updated Task", "status": "completed"}'
```

### Delete a Task
```bash
curl -X DELETE "http://localhost:8000/api/v1/tasks/1"
```

## Next Steps

1. Add authentication middleware for JWT token verification
2. Implement proper user management
3. Add comprehensive error handling
4. Create unit and integration tests
5. Set up proper logging
6. Add rate limiting for production use