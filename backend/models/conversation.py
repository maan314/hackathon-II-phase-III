"""
Conversation and Message models for AI Chat Agent system.
"""
from sqlmodel import SQLModel, Field, Relationship, Column
from sqlalchemy import JSON, String
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
        extra_data: Additional conversation metadata (JSON)
    """
    __tablename__ = "conversations"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: str = Field(index=True, max_length=255)
    title: Optional[str] = Field(default=None, max_length=500)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    extra_data: Optional[dict] = Field(default=None, sa_column=Column(JSON))

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
        tool_calls: Tool invocations made by agent (JSON)
        extra_data: Additional message metadata (JSON)
    """
    __tablename__ = "messages"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    conversation_id: UUID = Field(foreign_key="conversations.id", index=True)
    role: MessageRole = Field(sa_column=Column(String(20)))
    content: str = Field(min_length=1)
    timestamp: datetime = Field(default_factory=datetime.utcnow, index=True)
    tool_calls: Optional[List[dict]] = Field(default=None, sa_column=Column(JSON))
    extra_data: Optional[dict] = Field(default=None, sa_column=Column(JSON))

    # Relationship to conversation
    conversation: Optional[Conversation] = Relationship(back_populates="messages")
