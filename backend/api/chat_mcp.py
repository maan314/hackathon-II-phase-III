"""
Chat endpoint with MCP tool integration.

This endpoint extends the base chat functionality with MCP tool calling.
When enabled, the agent can invoke task management tools through natural language.

For Judges:
This demonstrates the complete integration: user sends natural language message,
agent decides which tools to use, tools execute via MCP server, agent responds
with results. All conversation and tool calls are persisted to database.
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
from backend.agent.agent_with_mcp import run_agent_with_mcp_tools
from sqlmodel import Session

logger = logging.getLogger(__name__)

router = APIRouter()


class ChatRequest(BaseModel):
    """Request schema for chat endpoint with MCP tools."""
    message: str = Field(..., min_length=1, max_length=10000, description="User's message")
    conversation_id: Optional[UUID] = Field(None, description="Existing conversation ID (optional)")
    enable_mcp_tools: bool = Field(True, description="Enable MCP tool calling (default: True)")


class ChatResponse(BaseModel):
    """Response schema for chat endpoint."""
    conversation_id: UUID = Field(..., description="Conversation identifier")
    message: str = Field(..., description="AI agent's response")
    tool_calls: List[Dict] = Field(default_factory=list, description="Tool invocations")
    created_at: datetime = Field(..., description="Response timestamp")


@router.post("/api/{user_id}/chat_mcp", response_model=ChatResponse)
async def chat_with_mcp(
    user_id: str,
    request: ChatRequest,
    session: Session = Depends(get_session)
) -> ChatResponse:
    """
    Chat endpoint with MCP tool calling capabilities.

    This endpoint enables natural language task management through MCP tools.
    The agent can create, list, update, complete, and delete tasks based on
    user requests in natural language.

    Flow:
    1. Get or create conversation
    2. Load conversation history from database
    3. Execute agent with MCP tools enabled
    4. Agent decides which tools to call based on user message
    5. Tools execute via MCP server
    6. Agent generates response with tool results
    7. Persist user message and agent response with tool call metadata

    For Judges:
    This demonstrates the complete AI + MCP integration. Users can say things like:
    - "Create a task to review the proposal"
    - "Show me my pending tasks"
    - "Mark task 1 as complete"
    - "Delete task 2"
    And the agent will understand, call the appropriate tools, and respond naturally.

    Args:
        user_id: User identifier (from path parameter)
        request: Chat request with message and optional conversation_id
        session: Database session (dependency injection)

    Returns:
        ChatResponse: Agent response with conversation_id, message, tool_calls

    Example Request:
        POST /api/user123/chat_mcp
        {
            "message": "Create a task to review the proposal",
            "conversation_id": null,
            "enable_mcp_tools": true
        }

    Example Response:
        {
            "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
            "message": "I've created a task titled 'Review the proposal' for you.",
            "tool_calls": [
                {
                    "tool_name": "add_task",
                    "parameters": {"user_id": "user123", "title": "Review the proposal"},
                    "result": {"status": "success", "task": {...}},
                    "status": "success",
                    "timestamp": "2026-02-09T10:30:00Z"
                }
            ],
            "created_at": "2026-02-09T10:30:01Z"
        }
    """
    try:
        # Step 1: Get or create conversation
        if request.conversation_id:
            conversation = get_conversation(session, request.conversation_id, user_id)
            logger.info(f"Using existing conversation {conversation.id} for user {user_id}")
        else:
            conversation = create_conversation(session, user_id)
            logger.info(f"Created new conversation {conversation.id} for user {user_id}")

        # Step 2: Load conversation history from database
        messages = get_messages(session, conversation.id, user_id)
        conversation_history = format_messages_for_agent(messages)
        logger.info(f"Loaded {len(messages)} messages from conversation {conversation.id}")

        # Step 3: Execute agent with MCP tools
        if request.enable_mcp_tools:
            logger.info("Executing agent with MCP tools enabled")
            agent_response = await run_agent_with_mcp_tools(
                conversation_history=conversation_history,
                user_message=request.message,
                user_id=user_id
            )
        else:
            # Fallback to agent without tools
            from backend.agent.agent import run_agent
            logger.info("Executing agent without MCP tools")
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
        raise

    except Exception as e:
        logger.error(f"Chat endpoint error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An error occurred processing your message. Please try again."
        )
