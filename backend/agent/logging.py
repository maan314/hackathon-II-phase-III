"""
Tool call logging utilities for AI Chat Agent system.

Captures and formats tool invocations for storage in Message.tool_calls field.
"""

from datetime import datetime
from typing import Dict, Any, Optional


def log_tool_call(
    tool_name: str,
    parameters: Dict[str, Any],
    result: Optional[Any] = None,
    status: str = "success",
    error: Optional[str] = None
) -> Dict:
    """
    Create a structured tool call log entry.

    Tool Call Format:
    {
        "tool_name": "create_task",
        "parameters": {"title": "Review proposal"},
        "result": {"task_id": 123, "title": "Review proposal"},
        "status": "success",
        "error": null,
        "timestamp": "2026-02-09T10:30:00Z"
    }

    Args:
        tool_name: Name of the tool invoked
        parameters: Parameters passed to the tool
        result: Tool execution result (if successful)
        status: "success" or "failure"
        error: Error message (if failed)

    Returns:
        Dict: Structured tool call log entry
    """
    return {
        "tool_name": tool_name,
        "parameters": parameters,
        "result": result if status == "success" else None,
        "status": status,
        "error": error,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }


def log_tool_call_success(
    tool_name: str,
    parameters: Dict[str, Any],
    result: Any
) -> Dict:
    """
    Log a successful tool call.

    Args:
        tool_name: Name of the tool invoked
        parameters: Parameters passed to the tool
        result: Tool execution result

    Returns:
        Dict: Structured tool call log entry
    """
    return log_tool_call(
        tool_name=tool_name,
        parameters=parameters,
        result=result,
        status="success",
        error=None
    )


def log_tool_call_failure(
    tool_name: str,
    parameters: Dict[str, Any],
    error: str
) -> Dict:
    """
    Log a failed tool call.

    Args:
        tool_name: Name of the tool invoked
        parameters: Parameters passed to the tool
        error: Error message

    Returns:
        Dict: Structured tool call log entry
    """
    return log_tool_call(
        tool_name=tool_name,
        parameters=parameters,
        result=None,
        status="failure",
        error=error
    )
