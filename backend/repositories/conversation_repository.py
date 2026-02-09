"""
Repository layer for Conversation and Message operations.

Provides data access methods with user isolation enforcement.
"""
from sqlmodel import Session, select
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from backend.models.conversation import Conversation, Message, MessageRole


class ConversationRepository:
    """
    Repository for conversation and message data access.

    All methods enforce user_id isolation to prevent cross-user data access.
    """

    def __init__(self, session: Session):
        """
        Initialize repository with database session.

        Args:
            session: SQLModel database session
        """
        self.session = session

    def create_conversation(self, user_id: str, title: Optional[str] = None) -> Conversation:
        """
        Create a new conversation for a user.

        Args:
            user_id: User identifier from JWT token
            title: Optional conversation title

        Returns:
            Created Conversation object
        """
        conversation = Conversation(
            user_id=user_id,
            title=title
        )
        self.session.add(conversation)
        self.session.commit()
        self.session.refresh(conversation)
        return conversation

    def get_conversation(self, conversation_id: UUID, user_id: str) -> Optional[Conversation]:
        """
        Get a conversation by ID with user isolation.

        Args:
            conversation_id: Conversation UUID
            user_id: User identifier for isolation check

        Returns:
            Conversation object if found and owned by user, None otherwise
        """
        statement = select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id
        )
        return self.session.exec(statement).first()

    def list_conversations(
        self,
        user_id: str,
        limit: int = 20,
        offset: int = 0
    ) -> List[Conversation]:
        """
        List conversations for a user, ordered by most recent first.

        Args:
            user_id: User identifier
            limit: Maximum number of conversations to return
            offset: Number of conversations to skip

        Returns:
            List of Conversation objects
        """
        statement = (
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(Conversation.updated_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(self.session.exec(statement).all())

    def add_message(
        self,
        conversation_id: UUID,
        role: MessageRole,
        content: str,
        tool_calls: Optional[List[dict]] = None,
        metadata: Optional[dict] = None
    ) -> Message:
        """
        Add a message to a conversation.

        Args:
            conversation_id: Parent conversation UUID
            role: Message role (user or assistant)
            content: Message text content
            tool_calls: Optional list of tool invocations
            metadata: Optional message metadata

        Returns:
            Created Message object
        """
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            tool_calls=tool_calls,
            metadata=metadata
        )
        self.session.add(message)

        # Update conversation's updated_at timestamp
        conversation = self.session.get(Conversation, conversation_id)
        if conversation:
            conversation.updated_at = datetime.utcnow()

        self.session.commit()
        self.session.refresh(message)
        return message

    def get_messages(
        self,
        conversation_id: UUID,
        limit: int = 50,
        offset: int = 0
    ) -> List[Message]:
        """
        Get messages for a conversation in chronological order.

        Args:
            conversation_id: Conversation UUID
            limit: Maximum number of messages to return
            offset: Number of messages to skip

        Returns:
            List of Message objects ordered by timestamp ascending
        """
        statement = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.timestamp.asc())
            .limit(limit)
            .offset(offset)
        )
        return list(self.session.exec(statement).all())

    def update_conversation_title(
        self,
        conversation_id: UUID,
        user_id: str,
        title: str
    ) -> Optional[Conversation]:
        """
        Update conversation title with user isolation check.

        Args:
            conversation_id: Conversation UUID
            user_id: User identifier for isolation check
            title: New conversation title

        Returns:
            Updated Conversation object if found and owned by user, None otherwise
        """
        conversation = self.get_conversation(conversation_id, user_id)
        if conversation:
            conversation.title = title
            conversation.updated_at = datetime.utcnow()
            self.session.add(conversation)
            self.session.commit()
            self.session.refresh(conversation)
        return conversation
