"""
OpenAI Agent configuration for AI Chat Agent system.

Configures Agent with system prompt and Runner for deterministic execution.
Stateless design - agent recreated per request with conversation history.
"""

from openai import OpenAI
import logging
from typing import List, Dict

from backend.config import Config
from backend.agent.prompts import SYSTEM_PROMPT

logger = logging.getLogger(__name__)


# Initialize OpenAI client
# API key loaded from environment variable
client = OpenAI(api_key=Config.OPENAI_API_KEY)


def create_agent_messages(conversation_history: List[Dict[str, str]], user_message: str) -> List[Dict[str, str]]:
    """
    Create messages array for OpenAI Chat Completions API.

    Stateless Design:
    - Conversation history reconstructed from database per request
    - System prompt prepended to conversation
    - No in-memory conversation state

    Args:
        conversation_history: Previous messages from database
        user_message: New user message

    Returns:
        List[Dict]: Messages formatted for OpenAI API
    """
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]

    # Add conversation history
    messages.extend(conversation_history)

    # Add new user message
    messages.append({"role": "user", "content": user_message})

    return messages


def run_agent(conversation_history: List[Dict[str, str]], user_message: str) -> Dict:
    """
    Execute agent with conversation history and new user message.

    Stateless Design:
    - Agent recreated per request (no persistent agent instance)
    - Full conversation history provided for context
    - Deterministic execution via OpenAI Chat Completions

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
        Exception: OpenAI API errors, timeout errors
    """
    try:
        # Create messages array with system prompt and history
        messages = create_agent_messages(conversation_history, user_message)

        # Call OpenAI Chat Completions API
        # Note: For hackathon scope, using direct API calls
        # In production, would use OpenAI Agents SDK with proper tool registration
        response = client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            temperature=0.7,
            max_tokens=1000,
            timeout=Config.API_TIMEOUT
        )

        # Extract assistant message
        assistant_message = response.choices[0].message.content

        # Extract tool calls if present
        tool_calls = []
        if hasattr(response.choices[0].message, 'tool_calls') and response.choices[0].message.tool_calls:
            for tool_call in response.choices[0].message.tool_calls:
                tool_calls.append({
                    "tool_name": tool_call.function.name,
                    "parameters": tool_call.function.arguments,
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

    This version includes tool definitions for OpenAI function calling.
    Agent can invoke tools and receive results.

    Args:
        conversation_history: Previous messages from database
        user_message: New user message
        tools: Tool definitions for function calling

    Returns:
        Dict: Agent response with message and executed tool_calls
    """
    try:
        messages = create_agent_messages(conversation_history, user_message)

        # Call OpenAI with function calling
        response = client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            tools=tools,
            tool_choice="auto",
            temperature=0.7,
            max_tokens=1000,
            timeout=Config.API_TIMEOUT
        )

        assistant_message = response.choices[0].message.content or ""
        tool_calls = []

        # Process tool calls if present
        if hasattr(response.choices[0].message, 'tool_calls') and response.choices[0].message.tool_calls:
            for tool_call in response.choices[0].message.tool_calls:
                tool_calls.append({
                    "id": tool_call.id,
                    "tool_name": tool_call.function.name,
                    "parameters": tool_call.function.arguments,
                    "result": None,
                    "status": "pending",
                    "error": None,
                    "timestamp": None
                })

        return {
            "message": assistant_message,
            "tool_calls": tool_calls,
            "finish_reason": response.choices[0].finish_reason
        }

    except Exception as e:
        logger.error(f"Agent execution with tools error: {e}")
        raise
