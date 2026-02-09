"""
Database models for MCP server.

Defines SQLModel entities for task management.
"""
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional
from enum import Enum


class TaskStatus(str, Enum):
    """Task status enumeration."""
    PENDING = "pending"
    COMPLETED = "completed"


class Task(SQLModel, table=True):
    """
    Task entity representing a todo item.
    
    Attributes:
        id: Unique task identifier (auto-generated)
        user_id: Owner of the task (indexed for user isolation)
        title: Task title (1-200 characters)
        description: Optional task description (max 2000 characters)
        status: Task status (pending or completed)
        due_date: Optional due date
        created_at: Timestamp when task was created
        updated_at: Timestamp when task was last modified
    """
    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True, max_length=255)
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)
    status: TaskStatus = Field(default=TaskStatus.PENDING)
    due_date: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "user_id": "user123",
                "title": "Review the proposal",
                "description": "Review and provide feedback on the Q4 proposal",
                "status": "pending",
                "due_date": "2026-02-15T17:00:00Z",
                "created_at": "2026-02-09T10:30:00Z",
                "updated_at": "2026-02-09T10:30:00Z"
            }
        }
