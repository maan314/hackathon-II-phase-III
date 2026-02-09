"""
Conversation and Message models for AI Chat Agent system.
"""
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional, List
from enum import Enum


class MessageRole(str, Enum):
    """Message role enum for user and assistant messages."""
    USER = "user"
    ASSISTANT = "assistant"


class Conversation(SQLModel, table=True):
    """
    Conversation model representing a chat thread between user and AI agent.

    Attributes:
        id: Unique conversation identifier
        user_id: User who owns this conversation
        title: Optional conversation title (auto-generated from first message)
        created_at: Conversation creation timestamp
        updated_at: Last update timestamp
        metadata: Additional conversation metadata (JSONB)
    """
    __tablename__ = "conversations"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: str = Field(index=True, max_length=255)
    title: Optional[str] = Field(default=None, max_length=500)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[dict] = Field(default=None, sa_column_kwargs={"type_": "JSONB"})

    # Relationship to messages
    messages: List["Message"] = Relationship(back_populates="conversation")


class Message(SQLModel, table=True):
    """
    Message model representing a single message in a conversation.

    Attributes:
        id: Unique message identifier
        conversation_id: Parent conversation reference
        role: Message sender role (user or assistant)
        content: Message text content
        timestamp: Message creation timestamp
        tool_calls: Tool invocations made by agent (JSONB)
        metadata: Additional message metadata (JSONB)
    """
    __tablename__ = "messages"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    conversation_id: UUID = Field(foreign_key="conversations.id", index=True)
    role: MessageRole = Field(sa_column_kwargs={"type_": "VARCHAR(20)"})
    content: str = Field(min_length=1)
    timestamp: datetime = Field(default_factory=datetime.utcnow, index=True)
    tool_calls: Optional[List[dict]] = Field(default=None, sa_column_kwargs={"type_": "JSONB"})
    metadata: Optional[dict] = Field(default=None, sa_column_kwargs={"type_": "JSONB"})

    # Relationship to conversation
    conversation: Optional[Conversation] = Relationship(back_populates="messages")
