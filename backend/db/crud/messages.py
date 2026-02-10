"""
CRUD operations for Message model.

All operations enforce user isolation through conversation ownership.
Stateless design - no in-memory caching, fresh queries per request.
"""

from uuid import UUID
from typing import List, Optional
from sqlmodel import Session, select
from datetime import datetime

from backend.db.models import Message, MessageRole
from backend.db.crud.conversations import get_conversation


def create_message(
    session: Session,
    conversation_id: UUID,
    user_id: str,
    role: MessageRole,
    content: str,
    tool_calls: Optional[List[dict]] = None
) -> Message:
    """
    Create a new message in a conversation.

    User Isolation:
    - Verifies user owns the conversation before creating message
    - Prevents users from adding messages to other users' conversations

    Stateless Design:
    - Message immediately persisted to database
    - Conversation updated_at timestamp updated via trigger

    Tool Call Logging:
    - tool_calls stored as JSON array for assistant messages
    - Includes tool name, parameters, result, status, timestamp

    Args:
        session: Database session
        conversation_id: Conversation UUID
        user_id: User identifier (enforces user isolation)
        role: Message role (user or assistant)
        content: Message text content
        tool_calls: Optional array of tool call objects (assistant only)

    Returns:
        Message: Newly created message

    Raises:
        HTTPException: 404 if conversation not found or user doesn't have access
    """
    # Verify user owns the conversation (user isolation)
    get_conversation(session, conversation_id, user_id)

    # Create message
    message = Message(
        conversation_id=conversation_id,
        role=role,
        content=content,
        tool_calls=tool_calls,
        created_at=datetime.utcnow()
    )

    session.add(message)
    session.commit()
    session.refresh(message)

    # Note: Conversation updated_at is automatically updated by database trigger

    return message


def get_messages(
    session: Session,
    conversation_id: UUID,
    user_id: str,
    limit: Optional[int] = None,
    offset: int = 0
) -> List[Message]:
    """
    Get all messages for a conversation in chronological order.

    User Isolation:
    - Verifies user owns the conversation before retrieving messages
    - Prevents users from accessing other users' messages

    Stateless Design:
    - Fresh query from database per request
    - No caching of message history
    - History reconstructed for each request

    Message Ordering:
    - Messages ordered by created_at ASC (chronological)
    - Ensures correct conversation flow for agent context

    Args:
        session: Database session
        conversation_id: Conversation UUID
        user_id: User identifier (enforces user isolation)
        limit: Optional maximum number of messages to return
        offset: Number of messages to skip (pagination)

    Returns:
        List[Message]: Messages in chronological order

    Raises:
        HTTPException: 404 if conversation not found or user doesn't have access
    """
    # Verify user owns the conversation (user isolation)
    get_conversation(session, conversation_id, user_id)

    # Query messages in chronological order
    statement = (
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())  # Chronological order
        .offset(offset)
    )

    if limit:
        statement = statement.limit(limit)

    messages = session.exec(statement).all()

    return list(messages)


def get_message(
    session: Session,
    message_id: UUID,
    user_id: str
) -> Message:
    """
    Get a specific message by ID with user isolation.

    User Isolation:
    - Verifies user owns the conversation containing the message
    - Prevents users from accessing other users' messages

    Args:
        session: Database session
        message_id: Message UUID
        user_id: User identifier (enforces user isolation)

    Returns:
        Message: The requested message

    Raises:
        HTTPException: 404 if message not found or user doesn't have access
    """
    from fastapi import HTTPException

    # Get message
    statement = select(Message).where(Message.id == message_id)
    message = session.exec(statement).first()

    if not message:
        raise HTTPException(
            status_code=404,
            detail=f"Message {message_id} not found"
        )

    # Verify user owns the conversation (user isolation)
    get_conversation(session, message.conversation_id, user_id)

    return message


def delete_message(
    session: Session,
    message_id: UUID,
    user_id: str
) -> bool:
    """
    Delete a specific message.

    User Isolation:
    - Verifies user owns the conversation before deletion

    Args:
        session: Database session
        message_id: Message UUID
        user_id: User identifier (enforces user isolation)

    Returns:
        bool: True if deleted successfully

    Raises:
        HTTPException: 404 if message not found or user doesn't have access
    """
    message = get_message(session, message_id, user_id)

    session.delete(message)
    session.commit()

    return True


def format_messages_for_agent(messages: List[Message]) -> List[dict]:
    """
    Format messages for Cohere Agent context.

    Converts Message models to the format expected by Cohere API:
    [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]

    Args:
        messages: List of Message models in chronological order

    Returns:
        List[dict]: Messages formatted for agent context
    """
    return [
        {
            "role": message.role.value,
            "content": message.content
        }
        for message in messages
    ]
