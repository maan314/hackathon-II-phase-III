"""
Cohere Agent configuration for AI Chat Agent system.

Configures Agent with system prompt for deterministic execution.
Stateless design - agent recreated per request with conversation history.
"""

import cohere
import logging
from typing import List, Dict

from backend.config import Config
from backend.agent.prompts import SYSTEM_PROMPT

logger = logging.getLogger(__name__)


# Initialize Cohere client
# API key loaded from environment variable
client = cohere.Client(api_key=Config.COHERE_API_KEY)


def create_agent_messages(conversation_history: List[Dict[str, str]], user_message: str) -> tuple:
    """
    Create chat history and message for Cohere Chat API.

    Stateless Design:
    - Conversation history reconstructed from database per request
    - System prompt used as preamble
    - No in-memory conversation state

    Args:
        conversation_history: Previous messages from database
        user_message: New user message

    Returns:
        tuple: (chat_history, user_message) formatted for Cohere API
    """
    # Convert to Cohere chat_history format
    chat_history = []
    for msg in conversation_history:
        role = "USER" if msg["role"] == "user" else "CHATBOT"
        chat_history.append({
            "role": role,
            "message": msg["content"]
        })

    return chat_history, user_message


def run_agent(conversation_history: List[Dict[str, str]], user_message: str) -> Dict:
    """
    Execute agent with conversation history and new user message.

    Stateless Design:
    - Agent recreated per request (no persistent agent instance)
    - Full conversation history provided for context
    - Deterministic execution via Cohere Chat API

    Tool Execution:
    - Agent determines which tools to call based on user message
    - Tools invoked via function calling
    - Tool results included in response

    Args:
        conversation_history: Previous messages from database
        user_message: New user message

    Returns:
        Dict: Agent response with message and tool_calls
            {
                "message": "Assistant response text",
                "tool_calls": [
                    {
                        "tool_name": "create_task",
                        "parameters": {"title": "..."},
                        "result": {...},
                        "status": "success",
                        "error": None,
                        "timestamp": "2026-02-09T10:30:00Z"
                    }
                ]
            }

    Raises:
        Exception: Cohere API errors, timeout errors
    """
    try:
        # Create chat history with conversation context
        chat_history, message = create_agent_messages(conversation_history, user_message)

        # Call Cohere Chat API
        response = client.chat(
            model=Config.AGENT_MODEL if hasattr(Config, 'AGENT_MODEL') else "command-r-08-2024",
            message=message,
            chat_history=chat_history,
            preamble=SYSTEM_PROMPT,
            temperature=0.7,
            max_tokens=1000
        )

        # Extract assistant message
        assistant_message = response.text

        # Extract tool calls if present
        tool_calls = []
        if hasattr(response, 'tool_calls') and response.tool_calls:
            for tool_call in response.tool_calls:
                tool_calls.append({
                    "tool_name": tool_call.name,
                    "parameters": tool_call.parameters,
                    "result": None,  # Would be populated after tool execution
                    "status": "pending",
                    "error": None,
                    "timestamp": None
                })

        return {
            "message": assistant_message,
            "tool_calls": tool_calls
        }

    except Exception as e:
        logger.error(f"Agent execution error: {e}")
        raise


def run_agent_with_tools(
    conversation_history: List[Dict[str, str]],
    user_message: str,
    tools: List[Dict]
) -> Dict:
    """
    Execute agent with tool definitions for function calling.

    This version includes tool definitions for Cohere tool calling.
    Agent can invoke tools and receive results.

    Args:
        conversation_history: Previous messages from database
        user_message: New user message
        tools: Tool definitions for function calling (Cohere format)

    Returns:
        Dict: Agent response with message and executed tool_calls
    """
    try:
        chat_history, message = create_agent_messages(conversation_history, user_message)

        # Call Cohere with tool calling
        response = client.chat(
            model=Config.AGENT_MODEL if hasattr(Config, 'AGENT_MODEL') else "command-r-08-2024",
            message=message,
            chat_history=chat_history,
            preamble=SYSTEM_PROMPT,
            tools=tools,
            temperature=0.7,
            max_tokens=1000
        )

        assistant_message = response.text or ""
        tool_calls = []

        # Process tool calls if present
        if hasattr(response, 'tool_calls') and response.tool_calls:
            for tool_call in response.tool_calls:
                tool_calls.append({
                    "id": getattr(tool_call, 'id', None),
                    "tool_name": tool_call.name,
                    "parameters": tool_call.parameters,
                    "result": None,
                    "status": "pending",
                    "error": None,
                    "timestamp": None
                })

        return {
            "message": assistant_message,
            "tool_calls": tool_calls,
            "finish_reason": getattr(response, 'finish_reason', 'COMPLETE')
        }

    except Exception as e:
        logger.error(f"Agent execution with tools error: {e}")
        raise
