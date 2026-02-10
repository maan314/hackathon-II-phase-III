from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlmodel import Session
from typing import List, Optional
from pydantic import BaseModel
from db.models import Task, TaskStatus
from db.crud.tasks import (
    create_task, list_tasks, get_task,
    update_task as update_task_crud,
    complete_task, reopen_task, delete_task
)
from database import get_session
from datetime import datetime
from core.security import verify_token

# ADD redirect_slashes=False HERE
router = APIRouter(prefix="/todos", tags=["todos"], redirect_slashes=False)

# Pydantic models for API requests/responses
class TodoCreate(BaseModel):
    title: str
    description: Optional[str] = None
    due_date: Optional[str] = None
    status: Optional[str] = "pending"

class TodoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[str] = None
    status: Optional[str] = None

class TodoRead(BaseModel):
    id: int
    title: str
    description: Optional[str]
    status: str
    is_completed: bool  # Add this for frontend compatibility
    due_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

def get_current_user(authorization: str = Header(..., description="Authorization header with Bearer token")):
    """Extract user ID from JWT token in Authorization header"""
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = authorization.removeprefix("Bearer ")

    payload = verify_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id: str = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return str(user_id)  # Return as string for Task model

@router.post("", response_model=TodoRead)  # Changed from "/" to ""
def create_new_todo(
    todo_create: TodoCreate,
    user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Create a new todo item for the authenticated user"""
    # Parse due_date if provided
    due_date = None
    if todo_create.due_date:
        try:
            due_date = datetime.fromisoformat(todo_create.due_date)
        except ValueError:
            pass

    task = create_task(
        session=session,
        user_id=user_id,
        title=todo_create.title,
        description=todo_create.description,
        due_date=due_date
    )
    return TodoRead(
        id=task.id,
        title=task.title,
        description=task.description,
        status=task.status.value if hasattr(task.status, 'value') else str(task.status),
        is_completed=(task.status.value if hasattr(task.status, 'value') else str(task.status)) == "completed",
        due_date=task.due_date,
        created_at=task.created_at,
        updated_at=task.updated_at
    )


@router.get("", response_model=List[TodoRead])  # Changed from "/" to ""
def read_todos(
    skip: int = 0,
    limit: int = 100,
    user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get all todo items for the authenticated user"""
    tasks = list_tasks(
        session=session,
        user_id=user_id,
        status=None,  # Get all tasks
        limit=limit,
        offset=skip
    )
    return [
        TodoRead(
            id=task.id,
            title=task.title,
            description=task.description,
            status=task.status.value if hasattr(task.status, 'value') else str(task.status),
            is_completed=(task.status.value if hasattr(task.status, 'value') else str(task.status)) == "completed",
            due_date=task.due_date,
            created_at=task.created_at,
            updated_at=task.updated_at
        )
        for task in tasks
    ]


@router.get("/{todo_id}", response_model=TodoRead)
def read_todo(
    todo_id: int,
    user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get a specific todo item by ID"""
    try:
        task = get_task(session=session, task_id=todo_id, user_id=user_id)
        return TodoRead(
            id=task.id,
            title=task.title,
            description=task.description,
            status=task.status.value if hasattr(task.status, 'value') else str(task.status),
            is_completed=(task.status.value if hasattr(task.status, 'value') else str(task.status)) == "completed",
            due_date=task.due_date,
            created_at=task.created_at,
            updated_at=task.updated_at
        )
    except HTTPException:
        raise HTTPException(status_code=404, detail="Todo not found")


@router.put("/{todo_id}", response_model=TodoRead)
def update_existing_todo(
    todo_id: int,
    todo_update: TodoUpdate,
    user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Update a specific todo item"""
    try:
        # Parse due_date if provided
        due_date = None
        if todo_update.due_date:
            try:
                due_date = datetime.fromisoformat(todo_update.due_date)
            except ValueError:
                pass

        # Handle status update (complete/uncomplete/reopen)
        if todo_update.status == "completed":
            task = complete_task(session=session, task_id=todo_id, user_id=user_id)
        elif todo_update.status == "pending":
            task = reopen_task(session=session, task_id=todo_id, user_id=user_id)
        else:
            # Regular update
            task = update_task_crud(
                session=session,
                task_id=todo_id,
                user_id=user_id,
                title=todo_update.title,
                description=todo_update.description,
                due_date=due_date
            )

        return TodoRead(
            id=task.id,
            title=task.title,
            description=task.description,
            status=task.status.value if hasattr(task.status, 'value') else str(task.status),
            is_completed=(task.status.value if hasattr(task.status, 'value') else str(task.status)) == "completed",
            due_date=task.due_date,
            created_at=task.created_at,
            updated_at=task.updated_at
        )
    except HTTPException:
        raise HTTPException(status_code=404, detail="Todo not found")


@router.delete("/{todo_id}")
def delete_existing_todo(
    todo_id: int,
    user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Delete a specific todo item"""
    try:
        delete_task(session=session, task_id=todo_id, user_id=user_id)
        return {"message": "Todo deleted successfully"}
    except HTTPException:
        raise HTTPException(status_code=404, detail="Todo not found")