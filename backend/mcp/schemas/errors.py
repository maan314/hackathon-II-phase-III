"""
Error handling schemas for MCP tools.

Provides consistent error response formatting.
"""
from typing import Dict, Any, Optional


class ToolError(Exception):
    """
    Custom exception for tool execution errors.
    
    Attributes:
        code: Error code (e.g., VALIDATION_ERROR, TASK_NOT_FOUND)
        message: Human-readable error message
        details: Optional additional context
    """
    
    def __init__(self, code: str, message: str, details: Optional[Dict[str, Any]] = None):
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(message)


def format_error_response(error: ToolError) -> Dict[str, Any]:
    """
    Format tool error as structured response.
    
    Args:
        error: ToolError instance
        
    Returns:
        Dictionary with status, error code, message, and details
    """
    return {
        "status": "error",
        "error": {
            "code": error.code,
            "message": error.message,
            "details": error.details
        }
    }


# Common error codes
class ErrorCodes:
    """Standard error codes for MCP tools."""
    VALIDATION_ERROR = "VALIDATION_ERROR"
    TASK_NOT_FOUND = "TASK_NOT_FOUND"
    DATABASE_ERROR = "DATABASE_ERROR"
    INTERNAL_ERROR = "INTERNAL_ERROR"
