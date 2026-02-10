"""
Database models for AI Chat Agent system.

This module defines SQLModel models for tasks.
Conversation and Message models are in backend/models/conversation.py
"""

from sqlmodel import SQLModel, Field, Column
from sqlalchemy import String
from datetime import datetime
from typing import Optional
from enum import Enum


class TaskStatus(str, Enum):
    """
    Enum for task status.

    - PENDING: Task is not yet completed
    - COMPLETED: Task has been completed
    """
    PENDING = "pending"
    COMPLETED = "completed"


class Task(SQLModel, table=True):
    """
    Task model representing a todo item for a user.

    Stateless Design:
    - No in-memory state maintained
    - All task data persisted to database
    - Tasks retrieved fresh from database per request

    User Isolation:
    - user_id indexed for fast filtering
    - All queries MUST filter by user_id to enforce isolation
    - Users can only access their own tasks

    MCP Tool Integration:
    - This model is accessed exclusively through MCP tools
    - Tools provide the only interface for task mutations
    - No direct database access outside of MCP tool handlers
    """
    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True, description="Unique task identifier")
    user_id: str = Field(index=True, max_length=255, description="Owner of the task (enforces user isolation)")
    title: str = Field(min_length=1, max_length=200, description="Task title (1-200 characters)")
    description: Optional[str] = Field(default=None, max_length=2000, description="Task description (optional, max 2000 characters)")
    status: TaskStatus = Field(default=TaskStatus.PENDING, sa_column=Column(String(20)), description="Task status (pending or completed)")
    due_date: Optional[datetime] = Field(default=None, description="Optional due date in ISO 8601 format")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="When task was created (auto-generated)")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last modification timestamp (auto-updated)")

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
