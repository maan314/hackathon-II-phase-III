"""
Complete Task Tool Handler.

Implements the complete_task MCP tool for marking tasks as completed.
"""
from fastapi import APIRouter
from sqlmodel import Session
from typing import Dict, Any
import time
import logging

from backend.mcp.db.engine import engine
from backend.mcp.db.crud import complete_task
from backend.mcp.schemas.inputs import CompleteTaskInput
from backend.mcp.schemas.outputs import TaskResponse
from backend.mcp.schemas.errors import ToolError, format_error_response
from backend.mcp.logging_config import log_tool_invocation

logger = logging.getLogger("mcp.tools")

router = APIRouter()


@router.post("/tools/complete_task")
async def complete_task_handler(input_data: CompleteTaskInput) -> Dict[str, Any]:
    """
    Complete Task Tool Handler.
    
    Marks a task as completed.
    
    Args:
        input_data: Validated input parameters
        
    Returns:
        Success response with updated task or error response
    """
    start_time = time.time()
    
    try:
        # Complete task using CRUD function
        with Session(engine) as session:
            task = complete_task(
                session=session,
                user_id=input_data.user_id,
                task_id=input_data.task_id
            )
        
        # Calculate execution time
        duration_ms = (time.time() - start_time) * 1000
        
        # Log successful invocation
        log_tool_invocation(
            logger=logger,
            tool_name="complete_task",
            user_id=input_data.user_id,
            result="success",
            duration_ms=duration_ms,
            task_id=task.id
        )
        
        # Format response
        task_response = TaskResponse(
            id=task.id,
            user_id=task.user_id,
            title=task.title,
            description=task.description,
            status=task.status.value,
            due_date=task.due_date,
            created_at=task.created_at,
            updated_at=task.updated_at
        )
        
        return {
            "status": "success",
            "task": task_response.model_dump()
        }
        
    except ToolError as e:
        duration_ms = (time.time() - start_time) * 1000
        log_tool_invocation(
            logger=logger,
            tool_name="complete_task",
            user_id=input_data.user_id,
            result="error",
            duration_ms=duration_ms,
            error_code=e.code
        )
        return format_error_response(e)
        
    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        logger.error(f"Unexpected error in complete_task: {str(e)}")
        log_tool_invocation(
            logger=logger,
            tool_name="complete_task",
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
