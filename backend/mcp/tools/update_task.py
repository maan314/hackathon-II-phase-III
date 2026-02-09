"""
Update Task Tool Handler.

Implements the update_task MCP tool for modifying task attributes.
"""
from fastapi import APIRouter
from sqlmodel import Session
from typing import Dict, Any
import time
import logging

from backend.mcp.db.engine import engine
from backend.mcp.db.crud import update_task
from backend.mcp.schemas.inputs import UpdateTaskInput
from backend.mcp.schemas.outputs import TaskResponse
from backend.mcp.schemas.errors import ToolError, format_error_response
from backend.mcp.logging_config import log_tool_invocation

logger = logging.getLogger("mcp.tools")

router = APIRouter()


@router.post("/tools/update_task")
async def update_task_handler(input_data: UpdateTaskInput) -> Dict[str, Any]:
    """
    Update Task Tool Handler.
    
    Modifies task attributes (partial update).
    
    Args:
        input_data: Validated input parameters
        
    Returns:
        Success response with updated task or error response
    """
    start_time = time.time()
    
    try:
        # Update task using CRUD function
        with Session(engine) as session:
            task = update_task(
                session=session,
                user_id=input_data.user_id,
                task_id=input_data.task_id,
                title=input_data.title,
                description=input_data.description,
                due_date=input_data.due_date
            )
        
        # Calculate execution time
        duration_ms = (time.time() - start_time) * 1000
        
        # Log successful invocation
        log_tool_invocation(
            logger=logger,
            tool_name="update_task",
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
            tool_name="update_task",
            user_id=input_data.user_id,
            result="error",
            duration_ms=duration_ms,
            error_code=e.code
        )
        return format_error_response(e)
        
    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        logger.error(f"Unexpected error in update_task: {str(e)}")
        log_tool_invocation(
            logger=logger,
            tool_name="update_task",
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
