"""
MCP Tool Handlers for Task Management.

These handlers implement the business logic for each MCP tool.
They are stateless, validate inputs, execute database operations,
and return structured responses.

Design Principles:
- Stateless: No in-memory state between invocations
- Pure CRUD: No AI logic, only database operations
- User Isolation: All operations filter by user_id
- Error Handling: Structured error responses
- Logging: All operations logged for observability
"""

import logging
from typing import Union
from datetime import datetime
from sqlmodel import Session
from fastapi import HTTPException

from backend.db.connection import get_session
from backend.db.crud.tasks import (
    create_task,
    list_tasks,
    complete_task,
    delete_task,
    update_task,
    get_task
)
from backend.db.models import Task
from backend.mcp.schemas.tool_schemas import (
    AddTaskInput,
    ListTasksInput,
    CompleteTaskInput,
    DeleteTaskInput,
    UpdateTaskInput,
    SuccessResponse,
    ListTasksResponse,
    DeleteTaskResponse,
    ErrorResponse,
    ErrorDetail,
    TaskOutput
)

logger = logging.getLogger(__name__)


def task_to_output(task: Task) -> TaskOutput:
    """
    Convert Task model to TaskOutput schema.

    Args:
        task: Task model instance

    Returns:
        TaskOutput: Pydantic schema for API response
    """
    return TaskOutput(
        id=task.id,
        user_id=task.user_id,
        title=task.title,
        description=task.description,
        status=task.status.value,
        due_date=task.due_date,
        created_at=task.created_at,
        updated_at=task.updated_at
    )


def handle_add_task(input_data: AddTaskInput) -> Union[SuccessResponse, ErrorResponse]:
    """
    Handle add_task tool invocation.

    Creates a new task for the user with the provided attributes.

    Stateless Design:
    - Fresh database session per invocation
    - No in-memory state maintained
    - Task immediately persisted to database

    User Isolation:
    - Task associated with user_id from input
    - Only this user can access this task

    Args:
        input_data: Validated input from AddTaskInput schema

    Returns:
        SuccessResponse: Contains created task
        ErrorResponse: If database error occurs

    Example:
        >>> input_data = AddTaskInput(
        ...     user_id="user123",
        ...     title="Review proposal",
        ...     description="Review Q4 proposal"
        ... )
        >>> response = handle_add_task(input_data)
        >>> response.status
        'success'
    """
    try:
        logger.info(f"add_task invoked for user {input_data.user_id}")

        # Get database session
        with next(get_session()) as session:
            # Create task via CRUD operation
            task = create_task(
                session=session,
                user_id=input_data.user_id,
                title=input_data.title,
                description=input_data.description,
                due_date=input_data.due_date
            )

            logger.info(f"Task {task.id} created for user {input_data.user_id}")

            # Return success response
            return SuccessResponse(
                status="success",
                task=task_to_output(task)
            )

    except Exception as e:
        logger.error(f"add_task error: {e}", exc_info=True)
        return ErrorResponse(
            status="error",
            error=ErrorDetail(
                code="DATABASE_ERROR",
                message="Failed to create task",
                details={"error": str(e)}
            )
        )


def handle_list_tasks(input_data: ListTasksInput) -> Union[ListTasksResponse, ErrorResponse]:
    """
    Handle list_tasks tool invocation.

    Retrieves all tasks for the user with optional status filtering.

    Stateless Design:
    - Fresh database session per invocation
    - No caching of task lists
    - Tasks retrieved fresh from database

    User Isolation:
    - Only returns tasks owned by user_id
    - No cross-user data access

    Args:
        input_data: Validated input from ListTasksInput schema

    Returns:
        ListTasksResponse: Contains array of tasks
        ErrorResponse: If database error occurs

    Example:
        >>> input_data = ListTasksInput(
        ...     user_id="user123",
        ...     status="pending"
        ... )
        >>> response = handle_list_tasks(input_data)
        >>> len(response.tasks)
        5
    """
    try:
        logger.info(f"list_tasks invoked for user {input_data.user_id}, status={input_data.status}")

        # Get database session
        with next(get_session()) as session:
            # List tasks via CRUD operation
            tasks = list_tasks(
                session=session,
                user_id=input_data.user_id,
                status=input_data.status if input_data.status != "all" else None
            )

            logger.info(f"Retrieved {len(tasks)} tasks for user {input_data.user_id}")

            # Return success response
            return ListTasksResponse(
                status="success",
                tasks=[task_to_output(task) for task in tasks]
            )

    except Exception as e:
        logger.error(f"list_tasks error: {e}", exc_info=True)
        return ErrorResponse(
            status="error",
            error=ErrorDetail(
                code="DATABASE_ERROR",
                message="Failed to retrieve tasks",
                details={"error": str(e)}
            )
        )


def handle_complete_task(input_data: CompleteTaskInput) -> Union[SuccessResponse, ErrorResponse]:
    """
    Handle complete_task tool invocation.

    Marks a task as completed.

    Stateless Design:
    - Fresh database session per invocation
    - Task status updated in database
    - updated_at timestamp automatically updated

    User Isolation:
    - Verifies user owns the task before completion
    - Returns 404 if task not found or belongs to different user

    Args:
        input_data: Validated input from CompleteTaskInput schema

    Returns:
        SuccessResponse: Contains updated task
        ErrorResponse: If task not found or database error

    Example:
        >>> input_data = CompleteTaskInput(
        ...     user_id="user123",
        ...     task_id=1
        ... )
        >>> response = handle_complete_task(input_data)
        >>> response.task.status
        'completed'
    """
    try:
        logger.info(f"complete_task invoked for user {input_data.user_id}, task_id={input_data.task_id}")

        # Get database session
        with next(get_session()) as session:
            # Complete task via CRUD operation
            task = complete_task(
                session=session,
                task_id=input_data.task_id,
                user_id=input_data.user_id
            )

            logger.info(f"Task {task.id} completed for user {input_data.user_id}")

            # Return success response
            return SuccessResponse(
                status="success",
                task=task_to_output(task)
            )

    except HTTPException as e:
        # Task not found or user doesn't have access
        logger.warning(f"complete_task not found: task_id={input_data.task_id}, user={input_data.user_id}")
        return ErrorResponse(
            status="error",
            error=ErrorDetail(
                code="TASK_NOT_FOUND",
                message=e.detail,
                details={
                    "task_id": input_data.task_id,
                    "user_id": input_data.user_id
                }
            )
        )

    except Exception as e:
        logger.error(f"complete_task error: {e}", exc_info=True)
        return ErrorResponse(
            status="error",
            error=ErrorDetail(
                code="DATABASE_ERROR",
                message="Failed to complete task",
                details={"error": str(e)}
            )
        )


def handle_delete_task(input_data: DeleteTaskInput) -> Union[DeleteTaskResponse, ErrorResponse]:
    """
    Handle delete_task tool invocation.

    Permanently deletes a task from the database.

    Stateless Design:
    - Fresh database session per invocation
    - Task permanently removed from database
    - No soft delete or archival

    User Isolation:
    - Verifies user owns the task before deletion
    - Returns 404 if task not found or belongs to different user

    Args:
        input_data: Validated input from DeleteTaskInput schema

    Returns:
        DeleteTaskResponse: Confirmation message
        ErrorResponse: If task not found or database error

    Example:
        >>> input_data = DeleteTaskInput(
        ...     user_id="user123",
        ...     task_id=1
        ... )
        >>> response = handle_delete_task(input_data)
        >>> response.message
        'Task deleted successfully'
    """
    try:
        logger.info(f"delete_task invoked for user {input_data.user_id}, task_id={input_data.task_id}")

        # Get database session
        with next(get_session()) as session:
            # Delete task via CRUD operation
            delete_task(
                session=session,
                task_id=input_data.task_id,
                user_id=input_data.user_id
            )

            logger.info(f"Task {input_data.task_id} deleted for user {input_data.user_id}")

            # Return success response
            return DeleteTaskResponse(
                status="success",
                message="Task deleted successfully",
                task_id=input_data.task_id
            )

    except HTTPException as e:
        # Task not found or user doesn't have access
        logger.warning(f"delete_task not found: task_id={input_data.task_id}, user={input_data.user_id}")
        return ErrorResponse(
            status="error",
            error=ErrorDetail(
                code="TASK_NOT_FOUND",
                message=e.detail,
                details={
                    "task_id": input_data.task_id,
                    "user_id": input_data.user_id
                }
            )
        )

    except Exception as e:
        logger.error(f"delete_task error: {e}", exc_info=True)
        return ErrorResponse(
            status="error",
            error=ErrorDetail(
                code="DATABASE_ERROR",
                message="Failed to delete task",
                details={"error": str(e)}
            )
        )


def handle_update_task(input_data: UpdateTaskInput) -> Union[SuccessResponse, ErrorResponse]:
    """
    Handle update_task tool invocation.

    Updates task attributes (partial update - only provided fields are updated).

    Stateless Design:
    - Fresh database session per invocation
    - Only provided fields are updated
    - updated_at timestamp automatically updated

    User Isolation:
    - Verifies user owns the task before update
    - Returns 404 if task not found or belongs to different user

    Args:
        input_data: Validated input from UpdateTaskInput schema

    Returns:
        SuccessResponse: Contains updated task
        ErrorResponse: If task not found or database error

    Example:
        >>> input_data = UpdateTaskInput(
        ...     user_id="user123",
        ...     task_id=1,
        ...     title="Review Q4 proposal"
        ... )
        >>> response = handle_update_task(input_data)
        >>> response.task.title
        'Review Q4 proposal'
    """
    try:
        logger.info(f"update_task invoked for user {input_data.user_id}, task_id={input_data.task_id}")

        # Get database session
        with next(get_session()) as session:
            # Update task via CRUD operation
            task = update_task(
                session=session,
                task_id=input_data.task_id,
                user_id=input_data.user_id,
                title=input_data.title,
                description=input_data.description,
                due_date=input_data.due_date
            )

            logger.info(f"Task {task.id} updated for user {input_data.user_id}")

            # Return success response
            return SuccessResponse(
                status="success",
                task=task_to_output(task)
            )

    except HTTPException as e:
        # Task not found or user doesn't have access
        logger.warning(f"update_task not found: task_id={input_data.task_id}, user={input_data.user_id}")
        return ErrorResponse(
            status="error",
            error=ErrorDetail(
                code="TASK_NOT_FOUND",
                message=e.detail,
                details={
                    "task_id": input_data.task_id,
                    "user_id": input_data.user_id
                }
            )
        )

    except Exception as e:
        logger.error(f"update_task error: {e}", exc_info=True)
        return ErrorResponse(
            status="error",
            error=ErrorDetail(
                code="DATABASE_ERROR",
                message="Failed to update task",
                details={"error": str(e)}
            )
        )
