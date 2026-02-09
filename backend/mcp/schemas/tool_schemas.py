"""
Pydantic schemas for MCP tool input/output validation.

These schemas define the contract between AI agents and MCP tools.
All schemas follow JSON Schema standards for compatibility.

Design Principles:
- Strict validation on all inputs
- Consistent response format (status + data or error)
- Clear error messages for validation failures
- User isolation enforced via user_id in all requests
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Literal
from datetime import datetime


# ============================================================================
# Input Schemas
# ============================================================================

class AddTaskInput(BaseModel):
    """
    Input schema for add_task tool.

    Creates a new task for a user with optional description and due date.
    """
    user_id: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="User identifier (required for user isolation)"
    )
    title: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Task title (1-200 characters)"
    )
    description: Optional[str] = Field(
        None,
        max_length=2000,
        description="Task description (optional, max 2000 characters)"
    )
    due_date: Optional[datetime] = Field(
        None,
        description="Due date in ISO 8601 format (optional)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user123",
                "title": "Review the proposal",
                "description": "Review and provide feedback on the Q4 proposal",
                "due_date": "2026-02-15T17:00:00Z"
            }
        }


class ListTasksInput(BaseModel):
    """
    Input schema for list_tasks tool.

    Retrieves tasks for a user with optional status filtering.
    """
    user_id: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="User identifier (required for user isolation)"
    )
    status: Literal["pending", "completed", "all"] = Field(
        "all",
        description="Filter by status (pending, completed, or all)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user123",
                "status": "pending"
            }
        }


class CompleteTaskInput(BaseModel):
    """
    Input schema for complete_task tool.

    Marks a task as completed.
    """
    user_id: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="User identifier (required for user isolation)"
    )
    task_id: int = Field(
        ...,
        ge=1,
        description="Task identifier (must be positive integer)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user123",
                "task_id": 1
            }
        }


class DeleteTaskInput(BaseModel):
    """
    Input schema for delete_task tool.

    Permanently deletes a task.
    """
    user_id: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="User identifier (required for user isolation)"
    )
    task_id: int = Field(
        ...,
        ge=1,
        description="Task identifier (must be positive integer)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user123",
                "task_id": 1
            }
        }


class UpdateTaskInput(BaseModel):
    """
    Input schema for update_task tool.

    Updates task attributes (partial update - only provided fields are updated).
    """
    user_id: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="User identifier (required for user isolation)"
    )
    task_id: int = Field(
        ...,
        ge=1,
        description="Task identifier (must be positive integer)"
    )
    title: Optional[str] = Field(
        None,
        min_length=1,
        max_length=200,
        description="New task title (optional)"
    )
    description: Optional[str] = Field(
        None,
        max_length=2000,
        description="New task description (optional)"
    )
    due_date: Optional[datetime] = Field(
        None,
        description="New due date in ISO 8601 format (optional)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user123",
                "task_id": 1,
                "title": "Review the Q4 proposal",
                "due_date": "2026-02-20T17:00:00Z"
            }
        }


# ============================================================================
# Output Schemas
# ============================================================================

class TaskOutput(BaseModel):
    """
    Task data structure for responses.

    Represents a single task with all attributes.
    """
    id: int = Field(..., description="Task identifier")
    user_id: str = Field(..., description="Owner of the task")
    title: str = Field(..., description="Task title")
    description: Optional[str] = Field(None, description="Task description")
    status: Literal["pending", "completed"] = Field(..., description="Task status")
    due_date: Optional[datetime] = Field(None, description="Due date")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "user_id": "user123",
                "title": "Review the proposal",
                "description": "Review and provide feedback on the Q4 proposal",
                "status": "pending",
                "due_date": "2026-02-15T17:00:00Z",
                "created_at": "2026-02-09T10:30:00Z",
                "updated_at": "2026-02-09T10:30:00Z"
            }
        }


class SuccessResponse(BaseModel):
    """
    Success response wrapper for single task operations.
    """
    status: Literal["success"] = "success"
    task: TaskOutput

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "task": {
                    "id": 1,
                    "user_id": "user123",
                    "title": "Review the proposal",
                    "status": "pending",
                    "created_at": "2026-02-09T10:30:00Z",
                    "updated_at": "2026-02-09T10:30:00Z"
                }
            }
        }


class ListTasksResponse(BaseModel):
    """
    Success response wrapper for list operations.
    """
    status: Literal["success"] = "success"
    tasks: List[TaskOutput]

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "tasks": [
                    {
                        "id": 1,
                        "user_id": "user123",
                        "title": "Review the proposal",
                        "status": "pending",
                        "created_at": "2026-02-09T10:30:00Z",
                        "updated_at": "2026-02-09T10:30:00Z"
                    }
                ]
            }
        }


class DeleteTaskResponse(BaseModel):
    """
    Success response for delete operations.
    """
    status: Literal["success"] = "success"
    message: str
    task_id: int

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "message": "Task deleted successfully",
                "task_id": 1
            }
        }


class ErrorDetail(BaseModel):
    """
    Error details structure.
    """
    code: str = Field(..., description="Error code (e.g., TASK_NOT_FOUND)")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[dict] = Field(None, description="Additional error context")


class ErrorResponse(BaseModel):
    """
    Error response wrapper for all error cases.
    """
    status: Literal["error"] = "error"
    error: ErrorDetail

    class Config:
        json_schema_extra = {
            "example": {
                "status": "error",
                "error": {
                    "code": "TASK_NOT_FOUND",
                    "message": "Task with id 123 not found for user user456",
                    "details": {
                        "task_id": 123,
                        "user_id": "user456"
                    }
                }
            }
        }
