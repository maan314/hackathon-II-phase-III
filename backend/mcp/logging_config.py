"""
Structured logging configuration for MCP server.

Provides JSON-formatted logging with request tracing.
"""
import logging
import json
from datetime import datetime
from typing import Any, Dict
import uuid


class JSONFormatter(logging.Formatter):
    """Custom formatter that outputs logs in JSON format."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        
        # Add extra fields if present
        if hasattr(record, "tool_name"):
            log_entry["tool_name"] = record.tool_name
        if hasattr(record, "user_id"):
            log_entry["user_id"] = record.user_id
        if hasattr(record, "duration_ms"):
            log_entry["duration_ms"] = record.duration_ms
        if hasattr(record, "request_id"):
            log_entry["request_id"] = record.request_id
        
        return json.dumps(log_entry)


def setup_logging(log_level: str = "INFO"):
    """
    Configure structured logging for MCP server.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
    """
    # Create logger
    logger = logging.getLogger("mcp")
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Create console handler with JSON formatter
    handler = logging.StreamHandler()
    handler.setFormatter(JSONFormatter())
    
    # Add handler to logger
    logger.addHandler(handler)
    
    return logger


def log_tool_invocation(
    logger: logging.Logger,
    tool_name: str,
    user_id: str,
    result: str,
    duration_ms: float,
    request_id: str = None,
    **kwargs
):
    """
    Log tool invocation with structured data.
    
    Args:
        logger: Logger instance
        tool_name: Name of the tool invoked
        user_id: User identifier
        result: Result status (success or error)
        duration_ms: Execution duration in milliseconds
        request_id: Optional request ID for tracing
        **kwargs: Additional fields to log
    """
    extra = {
        "tool_name": tool_name,
        "user_id": user_id,
        "result": result,
        "duration_ms": duration_ms,
        "request_id": request_id or str(uuid.uuid4()),
        **kwargs
    }
    
    logger.info(
        f"Tool invocation: {tool_name}",
        extra=extra
    )
