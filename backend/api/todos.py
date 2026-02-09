from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlmodel import Session
from typing import List
from models.todo import Todo, TodoCreate, TodoUpdate, TodoRead
from models.user import User
from services.todo_service import (
    create_todo, get_todos_for_user, get_todo_by_id,
    update_todo, delete_todo
)
from database import get_session
from datetime import datetime
from core.security import verify_token

# ADD redirect_slashes=False HERE
router = APIRouter(prefix="/todos", tags=["todos"], redirect_slashes=False)

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

    return int(user_id)

@router.post("", response_model=TodoRead)  # Changed from "/" to ""
def create_new_todo(
    todo_create: TodoCreate,
    user_id: int = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Create a new todo item for the authenticated user"""
    return create_todo(session=session, todo_create=todo_create, user_id=user_id)


@router.get("", response_model=List[TodoRead])  # Changed from "/" to ""
def read_todos(
    skip: int = 0,
    limit: int = 100,
    user_id: int = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get all todo items for the authenticated user"""
    return get_todos_for_user(session=session, user_id=user_id, skip=skip, limit=limit)


@router.get("/{todo_id}", response_model=TodoRead)
def read_todo(
    todo_id: int,
    user_id: int = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get a specific todo item by ID"""
    todo = get_todo_by_id(session=session, todo_id=todo_id, user_id=user_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo


@router.put("/{todo_id}", response_model=TodoRead)
def update_existing_todo(
    todo_id: int,
    todo_update: TodoUpdate,
    user_id: int = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Update a specific todo item"""
    updated_todo = update_todo(
        session=session,
        todo_id=todo_id,
        todo_update=todo_update,
        user_id=user_id
    )
    if not updated_todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return updated_todo


@router.delete("/{todo_id}")
def delete_existing_todo(
    todo_id: int,
    user_id: int = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Delete a specific todo item"""
    deleted = delete_todo(session=session, todo_id=todo_id, user_id=user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Todo not found")
    return {"message": "Todo deleted successfully"}