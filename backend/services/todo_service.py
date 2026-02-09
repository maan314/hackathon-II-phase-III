from sqlmodel import Session, select
from models.todo import Todo, TodoCreate, TodoUpdate
from models.user import User
from typing import List, Optional
from datetime import datetime

def create_todo(*, session: Session, todo_create: TodoCreate, user_id: int) -> Todo:
    """Create a new todo item for a user"""
    db_todo = Todo(
        title=todo_create.title,
        description=todo_create.description,
        is_completed=todo_create.is_completed,
        user_id=user_id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    session.add(db_todo)
    session.commit()
    session.refresh(db_todo)

    return db_todo

def get_todos_for_user(*, session: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Todo]:
    """Get all todos for a specific user"""
    statement = select(Todo).where(Todo.user_id == user_id).offset(skip).limit(limit)
    todos = session.exec(statement).all()
    return todos

def get_todo_by_id(*, session: Session, todo_id: int, user_id: int) -> Optional[Todo]:
    """Get a specific todo by ID for a user"""
    statement = select(Todo).where(Todo.id == todo_id, Todo.user_id == user_id)
    todo = session.exec(statement).first()
    return todo

def update_todo(*, session: Session, todo_id: int, todo_update: TodoUpdate, user_id: int) -> Optional[Todo]:
    """Update a todo item"""
    db_todo = get_todo_by_id(session=session, todo_id=todo_id, user_id=user_id)

    if not db_todo:
        return None

    todo_data = todo_update.dict(exclude_unset=True)
    for field, value in todo_data.items():
        setattr(db_todo, field, value)

    db_todo.updated_at = datetime.utcnow()
    session.add(db_todo)
    session.commit()
    session.refresh(db_todo)

    return db_todo

def delete_todo(*, session: Session, todo_id: int, user_id: int) -> bool:
    """Delete a todo item"""
    db_todo = get_todo_by_id(session=session, todo_id=todo_id, user_id=user_id)

    if not db_todo:
        return False

    session.delete(db_todo)
    session.commit()
    return True