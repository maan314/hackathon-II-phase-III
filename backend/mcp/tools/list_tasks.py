"""
List Tasks Tool Handler.

Implements the list_tasks MCP tool for retrieving user tasks.
"""
from fastapi import APIRouter
from sqlmodel import Session
from typing import Dict, Any
import time
import logging

from backend.mcp.db.engine import engine
from backend.mcp.db.crud import list_tasks
from backend.mcp.schemas.inputs import ListTasksInput
from backend.mcp.schemas.outputs import TaskResponse
from backend.mcp.schemas.errors import ToolError, format_error_response
from backend.mcp.logging_config import log_tool_invocation

logger = logging.getLogger("mcp.tools")

router = APIRouter()


@router.post("/tools/list_tasks")
async def list_tasks_handler(input_data: ListTasksInput) -> Dict[str, Any]:
    """
    List Tasks Tool Handler.
    
    Retrieves all tasks for a user with optional status filtering.
    
    Args:
        input_data: Validated input parameters
        
    Returns:
        Success response with task list or error response
    """
    start_time = time.time()
    
    try:
        # List tasks using CRUD function
        with Session(engine) as session:
            tasks = list_tasks(
                session=session,
                user_id=input_data.user_id,
                status=input_data.status,
                limit=100
            )
        
        # Calculate execution time
        duration_ms = (time.time() - start_time) * 1000
        
        # Log successful invocation
        log_tool_invocation(
            logger=logger,
            tool_name="list_tasks",
            user_id=input_data.user_id,
            result="success",
            duration_ms=duration_ms,
            task_count=len(tasks)
        )
        
        # Format response
        task_responses = [
            TaskResponse(
                id=task.id,
                user_id=task.user_id,
                title=task.title,
                description=task.description,
                status=task.status.value,
                due_date=task.due_date,
                created_at=task.created_at,
                updated_at=task.updated_at
            )
            for task in tasks
        ]
        
        return {
            "status": "success",
            "tasks": [task.model_dump() for task in task_responses]
        }
        
    except ToolError as e:
        duration_ms = (time.time() - start_time) * 1000
        log_tool_invocation(
            logger=logger,
            tool_name="list_tasks",
            user_id=input_data.user_id,
            result="error",
            duration_ms=duration_ms,
            error_code=e.code
        )
        return format_error_response(e)
        
    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        logger.error(f"Unexpected error in list_tasks: {str(e)}")
        log_tool_invocation(
            logger=logger,
            tool_name="list_tasks",
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
