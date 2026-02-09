"""
Add Task Tool Handler.

Implements the add_task MCP tool for creating new tasks.
"""
from fastapi import APIRouter, HTTPException
from sqlmodel import Session
from typing import Dict, Any
import time
import logging

from backend.mcp.db.engine import engine
from backend.mcp.db.crud import create_task
from backend.mcp.schemas.inputs import AddTaskInput
from backend.mcp.schemas.outputs import TaskResponse
from backend.mcp.schemas.errors import ToolError, format_error_response
from backend.mcp.logging_config import log_tool_invocation

logger = logging.getLogger("mcp.tools")

router = APIRouter()


@router.post("/tools/add_task")
async def add_task_handler(input_data: AddTaskInput) -> Dict[str, Any]:
    """
    Add Task Tool Handler.
    
    Creates a new task for a user with specified attributes.
    
    Args:
        input_data: Validated input parameters
        
    Returns:
        Success response with created task details or error response
    """
    start_time = time.time()
    
    try:
        # Create task using CRUD function
        with Session(engine) as session:
            task = create_task(
                session=session,
                user_id=input_data.user_id,
                title=input_data.title,
                description=input_data.description,
                due_date=input_data.due_date
            )
        
        # Calculate execution time
        duration_ms = (time.time() - start_time) * 1000
        
        # Log successful invocation
        log_tool_invocation(
            logger=logger,
            tool_name="add_task",
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
        # Calculate execution time
        duration_ms = (time.time() - start_time) * 1000
        
        # Log error
        log_tool_invocation(
            logger=logger,
            tool_name="add_task",
            user_id=input_data.user_id,
            result="error",
            duration_ms=duration_ms,
            error_code=e.code
        )
        
        return format_error_response(e)
        
    except Exception as e:
        # Calculate execution time
        duration_ms = (time.time() - start_time) * 1000
        
        # Log unexpected error
        logger.error(f"Unexpected error in add_task: {str(e)}")
        log_tool_invocation(
            logger=logger,
            tool_name="add_task",
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
