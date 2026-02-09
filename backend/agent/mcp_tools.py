"""
OpenAI Function Calling Tool Definitions for MCP Tools.

This module defines the tool schemas that OpenAI's function calling API
uses to understand when and how to invoke MCP tools.

Architecture:
- Tool definitions match MCP tool schemas
- Clear descriptions for AI agent understanding
- Parameter validation aligned with MCP server

For Judges:
These definitions bridge the AI agent and MCP tools. The agent uses
these schemas to understand what tools are available and how to call them.
When the agent decides to use a tool, it generates a function call that
matches these schemas.
"""

from typing import List, Dict, Any


# ============================================================================
# OpenAI Function Calling Tool Definitions
# ============================================================================

MCP_TOOLS: List[Dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "add_task",
            "description": "Create a new task for the user. Use this when the user asks to create, add, or make a new task or todo item.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "User identifier (automatically provided by the system)"
                    },
                    "title": {
                        "type": "string",
                        "description": "Task title (1-200 characters). Should be concise and descriptive."
                    },
                    "description": {
                        "type": "string",
                        "description": "Optional detailed description of the task (max 2000 characters)"
                    },
                    "due_date": {
                        "type": "string",
                        "description": "Optional due date in ISO 8601 format (e.g., '2026-02-15T17:00:00Z')"
                    }
                },
                "required": ["user_id", "title"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_tasks",
            "description": "Retrieve all tasks for the user with optional status filtering. Use this when the user asks to see, show, list, or view their tasks.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "User identifier (automatically provided by the system)"
                    },
                    "status": {
                        "type": "string",
                        "enum": ["pending", "completed", "all"],
                        "description": "Filter tasks by status. Use 'pending' for incomplete tasks, 'completed' for done tasks, or 'all' for everything. Default is 'all'."
                    }
                },
                "required": ["user_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "complete_task",
            "description": "Mark a task as completed. Use this when the user asks to complete, finish, mark as done, or check off a task.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "User identifier (automatically provided by the system)"
                    },
                    "task_id": {
                        "type": "integer",
                        "description": "The ID of the task to complete"
                    }
                },
                "required": ["user_id", "task_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_task",
            "description": "Permanently delete a task. Use this when the user asks to delete, remove, or get rid of a task.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "User identifier (automatically provided by the system)"
                    },
                    "task_id": {
                        "type": "integer",
                        "description": "The ID of the task to delete"
                    }
                },
                "required": ["user_id", "task_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_task",
            "description": "Update task attributes (partial update). Use this when the user asks to change, modify, edit, or update a task's title, description, or due date.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "User identifier (automatically provided by the system)"
                    },
                    "task_id": {
                        "type": "integer",
                        "description": "The ID of the task to update"
                    },
                    "title": {
                        "type": "string",
                        "description": "New task title (optional, only if changing)"
                    },
                    "description": {
                        "type": "string",
                        "description": "New task description (optional, only if changing)"
                    },
                    "due_date": {
                        "type": "string",
                        "description": "New due date in ISO 8601 format (optional, only if changing)"
                    }
                },
                "required": ["user_id", "task_id"]
            }
        }
    }
]


def get_tool_definitions() -> List[Dict[str, Any]]:
    """
    Get OpenAI function calling tool definitions.

    Returns:
        List[Dict]: Tool definitions for OpenAI API

    Example:
        >>> tools = get_tool_definitions()
        >>> len(tools)
        5
        >>> tools[0]["function"]["name"]
        'add_task'
    """
    return MCP_TOOLS


def get_tool_names() -> List[str]:
    """
    Get list of available tool names.

    Returns:
        List[str]: Tool names

    Example:
        >>> names = get_tool_names()
        >>> "add_task" in names
        True
    """
    return [tool["function"]["name"] for tool in MCP_TOOLS]
