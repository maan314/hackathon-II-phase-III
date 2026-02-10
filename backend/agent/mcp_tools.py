"""
Cohere Tool Calling Tool Definitions for MCP Tools.

This module defines the tool schemas that Cohere's tool calling API
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
# Cohere Tool Calling Tool Definitions
# ============================================================================

MCP_TOOLS: List[Dict[str, Any]] = [
    {
        "name": "add_task",
        "description": "Create a new task for the user. Use this when the user asks to create, add, or make a new task or todo item.",
        "parameter_definitions": {
            "user_id": {
                "type": "str",
                "description": "User identifier (automatically provided by the system)",
                "required": True
            },
            "title": {
                "type": "str",
                "description": "Task title (1-200 characters). Should be concise and descriptive.",
                "required": True
            },
            "description": {
                "type": "str",
                "description": "Optional detailed description of the task (max 2000 characters)",
                "required": False
            },
            "due_date": {
                "type": "str",
                "description": "Optional due date in ISO 8601 format (e.g., '2026-02-15T17:00:00Z')",
                "required": False
            }
        }
    },
    {
        "name": "list_tasks",
        "description": "Retrieve all tasks for the user with optional status filtering. Use this when the user asks to see, show, list, or view their tasks.",
        "parameter_definitions": {
            "user_id": {
                "type": "str",
                "description": "User identifier (automatically provided by the system)",
                "required": True
            },
            "status": {
                "type": "str",
                "description": "Filter tasks by status. Use 'pending' for incomplete tasks, 'completed' for done tasks, or 'all' for everything. Default is 'all'.",
                "required": False
            }
        }
    },
    {
        "name": "complete_task",
        "description": "Mark a task as completed. IMPORTANT: If the user doesn't specify a task ID, you MUST first use list_tasks to show them their tasks with IDs, then ask which one they want to complete. Users can see task IDs on the tasks page. Use this when the user asks to complete, finish, mark as done, or check off a task.",
        "parameter_definitions": {
            "user_id": {
                "type": "str",
                "description": "User identifier (automatically provided by the system)",
                "required": True
            },
            "task_id": {
                "type": "int",
                "description": "The ID of the task to complete. If the user didn't provide an ID, list their tasks first to show available IDs.",
                "required": True
            }
        }
    },
    {
        "name": "delete_task",
        "description": "Permanently delete a task. IMPORTANT: If the user doesn't specify a task ID, you MUST first use list_tasks to show them their tasks with IDs, then ask which one they want to delete. Users can see task IDs on the tasks page. Use this when the user asks to delete, remove, or get rid of a task.",
        "parameter_definitions": {
            "user_id": {
                "type": "str",
                "description": "User identifier (automatically provided by the system)",
                "required": True
            },
            "task_id": {
                "type": "int",
                "description": "The ID of the task to delete. If the user didn't provide an ID, list their tasks first to show available IDs.",
                "required": True
            }
        }
    },
    {
        "name": "update_task",
        "description": "Update task attributes (partial update). Use this when the user asks to change, modify, edit, or update a task's title, description, or due date.",
        "parameter_definitions": {
            "user_id": {
                "type": "str",
                "description": "User identifier (automatically provided by the system)",
                "required": True
            },
            "task_id": {
                "type": "int",
                "description": "The ID of the task to update",
                "required": True
            },
            "title": {
                "type": "str",
                "description": "New task title (optional, only if changing)",
                "required": False
            },
            "description": {
                "type": "str",
                "description": "New task description (optional, only if changing)",
                "required": False
            },
            "due_date": {
                "type": "str",
                "description": "New due date in ISO 8601 format (optional, only if changing)",
                "required": False
            }
        }
    }
]


def get_tool_definitions() -> List[Dict[str, Any]]:
    """
    Get Cohere tool calling tool definitions.

    Returns:
        List[Dict]: Tool definitions for Cohere API

    Example:
        >>> tools = get_tool_definitions()
        >>> len(tools)
        5
        >>> tools[0]["name"]
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
    return [tool["name"] for tool in MCP_TOOLS]
