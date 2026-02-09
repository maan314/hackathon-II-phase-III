from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime

class TodoBase(SQLModel):
    title: str
    description: Optional[str] = None
    is_completed: bool = False

class Todo(TodoBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship to user (using string reference to avoid circular import)
    user: "User" = Relationship(back_populates="todos")

class TodoCreate(TodoBase):
    pass

class TodoCreateWithUserId(TodoBase):
    user_id: int

class TodoUpdate(SQLModel):
    title: Optional[str] = None
    description: Optional[str] = None
    is_completed: Optional[bool] = None

class TodoRead(TodoBase):
    id: int
    created_at: datetime
    updated_at: datetime