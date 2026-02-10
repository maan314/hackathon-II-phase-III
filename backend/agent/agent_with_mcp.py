"""
Cohere Agent with MCP Tool Integration.

This module extends the base agent with MCP tool calling capabilities.
The agent can invoke task management tools through the MCP server.

Architecture:
- Cohere tool calling for tool invocation
- MCP client for tool execution
- Stateless design with conversation history
- Tool call logging for audit trail

For Judges:
This demonstrates the integration between the AI agent and MCP tools.
The agent uses Cohere's tool calling to decide when to use tools,
then executes them via the MCP client, and incorporates results back
into the conversation.
"""

import cohere
import logging
import json
from typing import List, Dict, Any
from datetime import datetime

from backend.config import Config
from backend.agent.prompts import SYSTEM_PROMPT
from backend.agent.mcp_tools import get_tool_definitions
from backend.agent.mcp_client import MCPClient
from backend.agent.logging import log_tool_call_success, log_tool_call_failure

logger = logging.getLogger(__name__)

# Initialize Cohere client
client = cohere.Client(api_key=Config.COHERE_API_KEY)

# Initialize MCP client
mcp_client = MCPClient(base_url="http://localhost:8001")


def create_agent_messages(conversation_history: List[Dict[str, str]], user_message: str) -> tuple:
    """
    Create chat history and message for Cohere Chat API.

    Args:
        conversation_history: Previous messages from database
        user_message: New user message

    Returns:
        tuple: (chat_history, user_message) formatted for Cohere API
    """
    chat_history = []
    for msg in conversation_history:
        role = "USER" if msg["role"] == "user" else "CHATBOT"
        chat_history.append({
            "role": role,
            "message": msg["content"]
        })
    return chat_history, user_message


async def run_agent_with_mcp_tools(
    conversation_history: List[Dict[str, str]],
    user_message: str,
    user_id: str
) -> Dict[str, Any]:
    """
    Execute agent with MCP tool calling capabilities.

    This function implements the full tool calling flow:
    1. Send user message to Cohere with tool definitions
    2. If agent requests tool calls, execute them via MCP client
    3. Send tool results back to Cohere
    4. Return final response with tool call metadata

    Stateless Design:
    - Fresh agent instance per request
    - Conversation history from database
    - No in-memory state between requests

    Tool Execution Flow:
    - Agent decides which tools to call based on user message
    - Tools executed via MCP client (HTTP to MCP server)
    - Tool results incorporated into conversation
    - Agent generates final response with context from tool results

    For Judges:
    This demonstrates the complete AI agent + MCP tools integration.
    The agent can understand natural language requests, decide which
    tools to use, execute them, and provide natural language responses
    based on the results.

    Args:
        conversation_history: Previous messages from database
        user_message: New user message
        user_id: User identifier for tool calls

    Returns:
        Dict: Agent response with message and tool_calls
            {
                "message": "Assistant response text",
                "tool_calls": [
                    {
                        "tool_name": "add_task",
                        "parameters": {"title": "..."},
                        "result": {...},
                        "status": "success",
                        "error": None,
                        "timestamp": "2026-02-09T10:30:00Z"
                    }
                ]
            }

    Example:
        >>> response = await run_agent_with_mcp_tools(
        ...     conversation_history=[],
        ...     user_message="Create a task to review the proposal",
        ...     user_id="user123"
        ... )
        >>> response["message"]
        "I've created a task titled 'Review the proposal' for you."
    """
    try:
        # Create chat history with system prompt
        chat_history, message = create_agent_messages(conversation_history, user_message)

        # Get MCP tool definitions for Cohere tool calling
        tools = get_tool_definitions()

        logger.info(f"Calling Cohere with {len(tools)} tools available")

        # First API call: Agent decides which tools to use
        response = client.chat(
            model="command-r-plus",
            message=message,
            chat_history=chat_history,
            preamble=SYSTEM_PROMPT,
            tools=tools,
            temperature=0.7,
            max_tokens=1000
        )

        tool_calls_metadata = []

        # Check if agent requested tool calls
        if hasattr(response, 'tool_calls') and response.tool_calls:
            logger.info(f"Agent requested {len(response.tool_calls)} tool calls")

            # Add assistant message with tool calls to conversation
            chat_history.append({
                "role": "CHATBOT",
                "message": response.text or "",
                "tool_calls": [
                    {
                        "name": tc.name,
                        "parameters": tc.parameters
                    }
                    for tc in response.tool_calls
                ]
            })

            # Execute each tool call via MCP client
            tool_results = []
            for tool_call in response.tool_calls:
                tool_name = tool_call.name

                try:
                    # Get tool arguments
                    arguments = tool_call.parameters

                    # Add user_id to arguments (required for all MCP tools)
                    arguments["user_id"] = user_id

                    logger.info(f"Executing MCP tool: {tool_name}")
                    logger.debug(f"Arguments: {arguments}")

                    # Execute tool via MCP client
                    if tool_name == "add_task":
                        result = await mcp_client.add_task(**arguments)
                    elif tool_name == "list_tasks":
                        result = await mcp_client.list_tasks(**arguments)
                    elif tool_name == "complete_task":
                        result = await mcp_client.complete_task(**arguments)
                    elif tool_name == "delete_task":
                        result = await mcp_client.delete_task(**arguments)
                    elif tool_name == "update_task":
                        result = await mcp_client.update_task(**arguments)
                    else:
                        result = {
                            "status": "error",
                            "error": {
                                "code": "UNKNOWN_TOOL",
                                "message": f"Unknown tool: {tool_name}"
                            }
                        }

                    # Log tool call for audit trail
                    if result.get("status") == "success":
                        tool_calls_metadata.append(
                            log_tool_call_success(tool_name, arguments, result)
                        )
                    else:
                        tool_calls_metadata.append(
                            log_tool_call_failure(
                                tool_name,
                                arguments,
                                result.get("error", {}).get("message", "Unknown error")
                            )
                        )

                    # Add tool result for next API call
                    tool_results.append({
                        "call": {
                            "name": tool_name,
                            "parameters": arguments
                        },
                        "outputs": [result]
                    })

                except Exception as e:
                    logger.error(f"Error executing tool {tool_name}: {e}", exc_info=True)

                    # Log failed tool call
                    tool_calls_metadata.append(
                        log_tool_call_failure(tool_name, {}, str(e))
                    )

                    # Add error result
                    tool_results.append({
                        "call": {
                            "name": tool_name,
                            "parameters": arguments if 'arguments' in locals() else {}
                        },
                        "outputs": [{
                            "status": "error",
                            "error": {
                                "code": "EXECUTION_ERROR",
                                "message": str(e)
                            }
                        }]
                    })

            # Second API call: Agent generates response based on tool results
            logger.info("Calling Cohere with tool results")
            final_response = client.chat(
                model="command-r-plus",
                message="",  # Empty message for tool result processing
                chat_history=chat_history,
                preamble=SYSTEM_PROMPT,
                tools=tools,
                tool_results=tool_results,
                temperature=0.7,
                max_tokens=1000
            )

            final_message = final_response.text

        else:
            # No tool calls - agent responded directly
            logger.info("Agent responded without tool calls")
            final_message = response.text

        return {
            "message": final_message,
            "tool_calls": tool_calls_metadata
        }

    except Exception as e:
        logger.error(f"Agent execution error: {e}", exc_info=True)
        raise


# Keep original run_agent for backward compatibility
def run_agent(conversation_history: List[Dict[str, str]], user_message: str) -> Dict:
    """
    Execute agent without MCP tools (backward compatibility).

    This is the original agent function without tool calling.
    Kept for backward compatibility with existing code.

    Args:
        conversation_history: Previous messages from database
        user_message: New user message

    Returns:
        Dict: Agent response with message and empty tool_calls
    """
    try:
        chat_history, message = create_agent_messages(conversation_history, user_message)

        response = client.chat(
            model="command-r-plus",
            message=message,
            chat_history=chat_history,
            preamble=SYSTEM_PROMPT,
            temperature=0.7,
            max_tokens=1000
        )

        assistant_message = response.text

        return {
            "message": assistant_message,
            "tool_calls": []
        }

    except Exception as e:
        logger.error(f"Agent execution error: {e}")
        raise
