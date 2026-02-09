"""
Delete Task Tool Handler.

Implements the delete_task MCP tool for permanently removing tasks.
"""
from fastapi import APIRouter
from sqlmodel import Session
from typing import Dict, Any
import time
import logging

from backend.mcp.db.engine import engine
from backend.mcp.db.crud import delete_task
from backend.mcp.schemas.inputs import DeleteTaskInput
from backend.mcp.schemas.errors import ToolError, format_error_response
from backend.mcp.logging_config import log_tool_invocation

logger = logging.getLogger("mcp.tools")

router = APIRouter()


@router.post("/tools/delete_task")
async def delete_task_handler(input_data: DeleteTaskInput) -> Dict[str, Any]:
    """
    Delete Task Tool Handler.
    
    Permanently removes a task from the database.
    
    Args:
        input_data: Validated input parameters
        
    Returns:
        Success response with confirmation or error response
    """
    start_time = time.time()
    
    try:
        # Delete task using CRUD function
        with Session(engine) as session:
            success = delete_task(
                session=session,
                user_id=input_data.user_id,
                task_id=input_data.task_id
            )
        
        # Calculate execution time
        duration_ms = (time.time() - start_time) * 1000
        
        # Log successful invocation
        log_tool_invocation(
            logger=logger,
            tool_name="delete_task",
            user_id=input_data.user_id,
            result="success",
            duration_ms=duration_ms,
            task_id=input_data.task_id
        )
        
        return {
            "status": "success",
            "message": "Task deleted successfully",
            "task_id": input_data.task_id
        }
        
    except ToolError as e:
        duration_ms = (time.time() - start_time) * 1000
        log_tool_invocation(
            logger=logger,
            tool_name="delete_task",
            user_id=input_data.user_id,
            result="error",
            duration_ms=duration_ms,
            error_code=e.code
        )
        return format_error_response(e)
        
    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        logger.error(f"Unexpected error in delete_task: {str(e)}")
        log_tool_invocation(
            logger=logger,
            tool_name="delete_task",
            user_id=input_data.user_id,
            result="error",
            duration_ms=duration_ms,
            error_code="INTERNAL_ERROR"
        )
        return format_error_response(
            ToolError(
                code="INTERNAL_ERROR",
                message="An unexpected error occurred",
                details={}
            )
        )
