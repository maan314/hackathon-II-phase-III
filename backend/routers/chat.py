"""
Chat API router for AI agent conversations.

Provides endpoint for sending messages to AI agent and receiving responses.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Header
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from uuid import UUID
from datetime import datetime
from sqlmodel import Session
import json
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from backend/.env
backend_dir = Path(__file__).parent.parent
env_path = backend_dir / '.env'
load_dotenv(dotenv_path=env_path)

from database import get_session
from core.security import verify_token
from repositories.conversation_repository import ConversationRepository
from services.agent_service import AgentService
from services.tool_handler import ToolHandler
from services.context_manager import ContextManager
from models.conversation import MessageRole

import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["chat"])


def get_current_user(authorization: str = Header(..., description="Authorization header with Bearer token")):
    """
    Extract user ID from JWT token in Authorization header.

    Uses existing auth system from backend.api.todos
    """
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = authorization.removeprefix("Bearer ")

    payload = verify_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id: str = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return str(user_id)  # Return as string for conversation storage


class ChatRequest(BaseModel):
    """
    Request model for chat endpoint.

    Attributes:
        message: User's message text (1-10000 characters)
        conversation_id: Optional existing conversation ID
    """
    message: str = Field(..., min_length=1, max_length=10000, description="User's message to the agent")
    conversation_id: Optional[UUID] = Field(None, description="Existing conversation ID (omit for new conversation)")


class ToolCallSummary(BaseModel):
    """Summary of a tool invocation."""
    tool_name: str
    status: str  # "success" or "error"


class ChatResponse(BaseModel):
    """
    Response model for chat endpoint.

    Attributes:
        response: Agent's response message
        conversation_id: Conversation identifier
        message_id: Message identifier
        timestamp: Response timestamp
        tool_calls: Optional list of tool invocations
    """
    response: str = Field(..., description="Agent's response message")
    conversation_id: UUID = Field(..., description="Conversation identifier")
    message_id: UUID = Field(..., description="Message identifier")
    timestamp: str = Field(..., description="Response timestamp (ISO 8601)")
    tool_calls: Optional[List[ToolCallSummary]] = Field(None, description="Tool invocations made (if any)")


# Initialize services (singleton pattern)
agent_service = AgentService()
context_manager = ContextManager()


@router.post("/{user_id}/chat", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def send_chat_message(
    user_id: str,
    request: ChatRequest,
    current_user: str = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Send a message to the AI agent and receive a response.

    This endpoint handles:
    - Creating new conversations or continuing existing ones
    - Loading conversation history for context
    - Processing messages with AI agent
    - Invoking tools for task operations
    - Persisting all messages to database

    Args:
        user_id: User identifier from path parameter
        request: Chat request with message and optional conversation_id
        current_user: Authenticated user from JWT token
        session: Database session

    Returns:
        ChatResponse with agent's response and metadata

    Raises:
        HTTPException 400: Invalid request format
        HTTPException 401: Unauthenticated request
        HTTPException 403: User trying to access another user's conversation
        HTTPException 404: Conversation not found
        HTTPException 500: Internal server error
        HTTPException 504: Agent processing timeout
    """
    try:
        # T028 & T029: Validate user_id matches authenticated user
        if user_id != current_user:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this conversation"
            )

        # T036: Input validation (message length already validated by Pydantic)
        # Additional validation for conversation_id format is handled by Pydantic UUID type

        repo = ConversationRepository(session)

        # T030: Get or create conversation
        if request.conversation_id:
            conversation = repo.get_conversation(request.conversation_id, user_id)
            if not conversation:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Conversation not found"
                )
        else:
            # Create new conversation
            conversation = repo.create_conversation(user_id)

        # T031: Persist user message
        user_message = repo.add_message(
            conversation_id=conversation.id,
            role=MessageRole.USER,
            content=request.message
        )

        # T032: Retrieve and format conversation history
        messages = repo.get_messages(conversation.id, limit=100)

        # Log conversation context
        logger.info(f"Processing chat request - User: {user_id}, Conversation: {conversation.id}, History: {len(messages)} messages")

        # Exclude the current user message from history (it's already in the context)
        history_messages = [
            {"role": msg.role.value if hasattr(msg.role, 'value') else str(msg.role), "content": msg.content}
            for msg in messages[:-1]  # Exclude last message (current one)
        ]

        # Apply context window management
        history_messages = context_manager.prepare_context(history_messages)

        # T033: Process message with agent (with session for tool execution)
        try:
            logger.info(f"Invoking AI agent - User: {user_id}, Message length: {len(request.message)}")
            agent_response = await agent_service.process_message(
                user_message=request.message,
                conversation_history=history_messages,
                user_id=user_id,
                session=session  # Pass session for tool execution
            )
            tool_calls = agent_response.get('tool_calls') or []
            logger.info(f"Agent response received - User: {user_id}, Response length: {len(agent_response.get('content', ''))}, Tool calls: {len(tool_calls)}")
        except Exception as e:
            # Log full traceback for debugging
            import traceback
            logger.error(f"AI service error: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")

            # T037: Handle Cohere API failures
            if "timeout" in str(e).lower():
                raise HTTPException(
                    status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                    detail="Request processing took too long. Please try again with a simpler message."
                )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"AI service error: {str(e)}"
            )

        # Handle tool calls if present (for metadata only - execution happens in agent_service)
        tool_call_summaries = []
        if agent_response.get("tool_calls"):
            for tool_call in agent_response["tool_calls"]:
                tool_call_summaries.append(ToolCallSummary(
                    tool_name=tool_call["name"],
                    status="success"  # Tools already executed in agent_service
                ))

        # T034: Persist agent response with tool_calls metadata
        assistant_message = repo.add_message(
            conversation_id=conversation.id,
            role=MessageRole.ASSISTANT,
            content=agent_response.get("content", ""),
            tool_calls=[
                {
                    "tool_name": tc.tool_name,
                    "status": tc.status
                }
                for tc in tool_call_summaries
            ] if tool_call_summaries else None
        )

        # T035: Format response
        return ChatResponse(
            response=agent_response.get("content", ""),
            conversation_id=conversation.id,
            message_id=assistant_message.id,
            timestamp=assistant_message.timestamp.isoformat(),
            tool_calls=tool_call_summaries if tool_call_summaries else None
        )

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # T038: Handle database and other failures
        logger.error(f"Chat endpoint error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to process request. Please try again later."
        )
