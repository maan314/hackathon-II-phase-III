"""
CRUD operations for Conversation model.

All operations enforce user isolation - queries MUST filter by user_id.
Stateless design - no in-memory caching, fresh queries per request.
"""

from uuid import UUID
from typing import List, Optional
from sqlmodel import Session, select
from datetime import datetime
from fastapi import HTTPException

from backend.db.models import Conversation


def create_conversation(session: Session, user_id: str) -> Conversation:
    """
    Create a new conversation for a user.

    Stateless Design:
    - No session state maintained
    - Conversation immediately persisted to database

    Args:
        session: Database session
        user_id: User identifier (enforces user isolation)

    Returns:
        Conversation: Newly created conversation

    Raises:
        Exception: Database errors
    """
    conversation = Conversation(
        user_id=user_id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    session.add(conversation)
    session.commit()
    session.refresh(conversation)

    return conversation


def get_conversation(session: Session, conversation_id: UUID, user_id: str) -> Conversation:
    """
    Get a conversation by ID with user isolation.

    User Isolation:
    - MUST filter by both conversation_id AND user_id
    - Prevents users from accessing other users' conversations

    Stateless Design:
    - Fresh query from database per request
    - No caching or in-memory storage

    Args:
        session: Database session
        conversation_id: Conversation UUID
        user_id: User identifier (enforces user isolation)

    Returns:
        Conversation: The requested conversation

    Raises:
        HTTPException: 404 if conversation not found or user doesn't have access
    """
    statement = select(Conversation).where(
        Conversation.id == conversation_id,
        Conversation.user_id == user_id  # User isolation enforcement
    )

    conversation = session.exec(statement).first()

    if not conversation:
        raise HTTPException(
            status_code=404,
            detail=f"Conversation {conversation_id} not found"
        )

    return conversation


def list_conversations(
    session: Session,
    user_id: str,
    limit: int = 50,
    offset: int = 0
) -> List[Conversation]:
    """
    List conversations for a user, ordered by most recent activity.

    User Isolation:
    - MUST filter by user_id
    - Only returns conversations owned by the user

    Stateless Design:
    - Fresh query from database per request
    - No caching of conversation lists

    Args:
        session: Database session
        user_id: User identifier (enforces user isolation)
        limit: Maximum number of conversations to return
        offset: Number of conversations to skip (pagination)

    Returns:
        List[Conversation]: User's conversations ordered by updated_at DESC
    """
    statement = (
        select(Conversation)
        .where(Conversation.user_id == user_id)  # User isolation enforcement
        .order_by(Conversation.updated_at.desc())
        .limit(limit)
        .offset(offset)
    )

    conversations = session.exec(statement).all()

    return list(conversations)


def update_conversation_timestamp(
    session: Session,
    conversation_id: UUID,
    user_id: str
) -> Conversation:
    """
    Update conversation's updated_at timestamp.

    Called when new messages are added to maintain accurate activity tracking.

    User Isolation:
    - MUST verify user owns the conversation

    Args:
        session: Database session
        conversation_id: Conversation UUID
        user_id: User identifier (enforces user isolation)

    Returns:
        Conversation: Updated conversation

    Raises:
        HTTPException: 404 if conversation not found or user doesn't have access
    """
    conversation = get_conversation(session, conversation_id, user_id)
    conversation.updated_at = datetime.utcnow()

    session.add(conversation)
    session.commit()
    session.refresh(conversation)

    return conversation


def delete_conversation(
    session: Session,
    conversation_id: UUID,
    user_id: str
) -> bool:
    """
    Delete a conversation and all its messages (cascade).

    User Isolation:
    - MUST verify user owns the conversation before deletion

    Args:
        session: Database session
        conversation_id: Conversation UUID
        user_id: User identifier (enforces user isolation)

    Returns:
        bool: True if deleted successfully

    Raises:
        HTTPException: 404 if conversation not found or user doesn't have access
    """
    conversation = get_conversation(session, conversation_id, user_id)

    session.delete(conversation)
    session.commit()

    return True
