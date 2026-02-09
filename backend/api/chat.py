"""
Chat endpoint for AI Chat Agent system.

Implements stateless POST /api/{user_id}/chat endpoint.
Each request reconstructs conversation history from database.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional, List, Dict
from datetime import datetime
import logging

from backend.db.connection import get_session
from backend.db.crud.conversations import create_conversation, get_conversation
from backend.db.crud.messages import create_message, get_messages, format_messages_for_agent
from backend.db.models import MessageRole
from backend.agent.agent import run_agent
from sqlmodel import Session

logger = logging.getLogger(__name__)

router = APIRouter()


class ChatRequest(BaseModel):
    """
    Request schema for chat endpoint.

    Stateless Design:
    - conversation_id optional (creates new if not provided)
    - No session state maintained between requests
    """
    message: str = Field(..., min_length=1, max_length=10000, description="User's message")
    conversation_id: Optional[UUID] = Field(None, description="Existing conversation ID (optional)")

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Create a task to review the proposal",
                "conversation_id": None
            }
        }


class ChatResponse(BaseModel):
    """
    Response schema for chat endpoint.

    Returns:
    - conversation_id: For client to track conversation
    - message: AI agent's response
    - tool_calls: Array of tool invocations (for audit trail)
    - created_at: Response timestamp
    """
    conversation_id: UUID = Field(..., description="Conversation identifier")
    message: str = Field(..., description="AI agent's response")
    tool_calls: List[Dict] = Field(default_factory=list, description="Tool invocations")
    created_at: datetime = Field(..., description="Response timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
                "message": "I've created a task titled 'Review the proposal' for you.",
                "tool_calls": [
                    {
                        "tool_name": "create_task",
                        "parameters": {"title": "Review the proposal"},
                        "result": {"task_id": 123},
                        "status": "success",
                        "error": None,
                        "timestamp": "2026-02-09T10:30:00Z"
                    }
                ],
                "created_at": "2026-02-09T10:30:01Z"
            }
        }


@router.post("/api/{user_id}/chat", response_model=ChatResponse)
async def chat(
    user_id: str,
    request: ChatRequest,
    session: Session = Depends(get_session)
) -> ChatResponse:
    """
    Stateless chat endpoint for AI agent conversations.

    Stateless Design:
    - No in-memory session state
    - Conversation history reconstructed from database per request
    - Fresh agent instance created per request

    Flow:
    1. Get or create conversation
    2. Load conversation history from database
    3. Execute agent with history + new message
    4. Persist user message and agent response
    5. Return response with tool_calls

    User Isolation:
    - user_id enforced in all database queries
    - Users can only access their own conversations

    Args:
        user_id: User identifier (from path parameter)
        request: Chat request with message and optional conversation_id
        session: Database session (dependency injection)

    Returns:
        ChatResponse: Agent response with conversation_id, message, tool_calls

    Raises:
        HTTPException: 400 for invalid input, 404 for conversation not found,
                      500 for agent or database errors
    """
    try:
        # Step 1: Get or create conversation
        # Stateless: Fresh query from database
        if request.conversation_id:
            # Existing conversation - verify user owns it
            conversation = get_conversation(session, request.conversation_id, user_id)
            logger.info(f"Using existing conversation {conversation.id} for user {user_id}")
        else:
            # New conversation
            conversation = create_conversation(session, user_id)
            logger.info(f"Created new conversation {conversation.id} for user {user_id}")

        # Step 2: Load conversation history from database
        # Stateless: History reconstructed per request, no caching
        messages = get_messages(session, conversation.id, user_id)
        conversation_history = format_messages_for_agent(messages)
        logger.info(f"Loaded {len(messages)} messages from conversation {conversation.id}")

        # Step 3: Execute agent with history + new message
        # Stateless: Fresh agent instance per request
        agent_response = run_agent(conversation_history, request.message)
        logger.info(f"Agent executed for conversation {conversation.id}")

        # Step 4: Persist user message
        user_message = create_message(
            session=session,
            conversation_id=conversation.id,
            user_id=user_id,
            role=MessageRole.USER,
            content=request.message,
            tool_calls=None
        )
        logger.info(f"Persisted user message {user_message.id}")

        # Step 5: Persist agent response with tool_calls
        assistant_message = create_message(
            session=session,
            conversation_id=conversation.id,
            user_id=user_id,
            role=MessageRole.ASSISTANT,
            content=agent_response["message"],
            tool_calls=agent_response.get("tool_calls", [])
        )
        logger.info(f"Persisted assistant message {assistant_message.id}")

        # Step 6: Return response
        return ChatResponse(
            conversation_id=conversation.id,
            message=agent_response["message"],
            tool_calls=agent_response.get("tool_calls", []),
            created_at=assistant_message.created_at
        )

    except HTTPException:
        # Re-raise HTTP exceptions (404, 403, etc.)
        raise

    except Exception as e:
        logger.error(f"Chat endpoint error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An error occurred processing your message. Please try again."
        )


@router.get("/api/{user_id}/conversations")
async def list_user_conversations(
    user_id: str,
    limit: int = 50,
    offset: int = 0,
    session: Session = Depends(get_session)
):
    """
    List conversations for a user.

    User Isolation:
    - Only returns conversations owned by user_id

    Args:
        user_id: User identifier
        limit: Maximum conversations to return
        offset: Pagination offset
        session: Database session

    Returns:
        List of conversations
    """
    from backend.db.crud.conversations import list_conversations

    conversations = list_conversations(session, user_id, limit, offset)

    return {
        "conversations": [
            {
                "id": str(conv.id),
                "created_at": conv.created_at.isoformat(),
                "updated_at": conv.updated_at.isoformat()
            }
            for conv in conversations
        ]
    }


@router.get("/api/{user_id}/conversations/{conversation_id}/messages")
async def get_conversation_messages(
    user_id: str,
    conversation_id: UUID,
    session: Session = Depends(get_session)
):
    """
    Get all messages for a conversation.

    User Isolation:
    - Verifies user owns the conversation

    Args:
        user_id: User identifier
        conversation_id: Conversation UUID
        session: Database session

    Returns:
        List of messages in chronological order
    """
    messages = get_messages(session, conversation_id, user_id)

    return {
        "messages": [
            {
                "id": str(msg.id),
                "role": msg.role.value,
                "content": msg.content,
                "tool_calls": msg.tool_calls,
                "created_at": msg.created_at.isoformat()
            }
            for msg in messages
        ]
    }
