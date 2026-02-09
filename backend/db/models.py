"""
Database models for AI Chat Agent system.

This module defines SQLModel models for conversations and messages.
All models are designed for stateless operation - no in-memory session state.
Each request reconstructs conversation history from the database.
"""

from sqlmodel import SQLModel, Field, Relationship, Column
from sqlalchemy import JSON
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional, List
from enum import Enum


class MessageRole(str, Enum):
    """
    Enum for message roles in a conversation.

    - USER: Message from the user
    - ASSISTANT: Message from the AI agent
    """
    USER = "user"
    ASSISTANT = "assistant"


class TaskStatus(str, Enum):
    """
    Enum for task status.

    - PENDING: Task is not yet completed
    - COMPLETED: Task has been completed
    """
    PENDING = "pending"
    COMPLETED = "completed"


class Conversation(SQLModel, table=True):
    """
    Conversation model representing a chat session between user and AI agent.

    Stateless Design:
    - No in-memory session state maintained
    - All conversation data persisted to database
    - Conversation history reconstructed per request

    User Isolation:
    - user_id indexed for fast filtering
    - All queries MUST filter by user_id to enforce isolation
    """
    __tablename__ = "conversations"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: str = Field(index=True, max_length=255, description="Owner of the conversation")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="When conversation was created")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last message timestamp")
    metadata: Optional[dict] = Field(default=None, sa_column=Column(JSON), description="Optional metadata")

    # Relationship to messages (one-to-many)
    messages: List["Message"] = Relationship(back_populates="conversation")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "user_id": "user123",
                "created_at": "2026-02-09T10:30:00Z",
                "updated_at": "2026-02-09T10:30:00Z",
                "metadata": {}
            }
        }


class Message(SQLModel, table=True):
    """
    Message model representing a single message in a conversation.

    Stateless Design:
    - Messages persisted immediately after creation
    - No caching or in-memory storage
    - Retrieved fresh from database for each request

    Tool Call Logging:
    - tool_calls field stores array of tool invocations
    - Only present for assistant messages
    - Includes tool name, parameters, result, status, timestamp
    """
    __tablename__ = "messages"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    conversation_id: UUID = Field(foreign_key="conversations.id", index=True, description="Reference to conversation")
    role: MessageRole = Field(sa_column_kwargs={"type_": "VARCHAR(20)"}, description="Message sender (user or assistant)")
    content: str = Field(max_length=10000, description="Message text content")
    tool_calls: Optional[List[dict]] = Field(
        default=None,
        sa_column=Column(JSON),
        description="Array of tool call objects (assistant only)"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True, description="When message was created")

    # Relationship to conversation (many-to-one)
    conversation: Conversation = Relationship(back_populates="messages")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "660e8400-e29b-41d4-a716-446655440001",
                "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
                "role": "user",
                "content": "Create a task to review the proposal",
                "tool_calls": None,
                "created_at": "2026-02-09T10:30:00Z"
            }
        }


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
    status: TaskStatus = Field(default=TaskStatus.PENDING, sa_column_kwargs={"type_": "VARCHAR(20)"}, description="Task status (pending or completed)")
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
