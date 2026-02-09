"""
Output schemas for MCP tools.

Defines Pydantic models for tool responses.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict
from datetime import datetime


class TaskResponse(BaseModel):
    """Response schema for a single task."""
    id: int = Field(..., description="Task ID")
    user_id: str = Field(..., description="User identifier")
    title: str = Field(..., description="Task title")
    description: Optional[str] = Field(None, description="Task description")
    status: str = Field(..., description="Task status (pending or completed)")
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


class TaskListResponse(BaseModel):
    """Response schema for list of tasks."""
    tasks: List[TaskResponse] = Field(..., description="List of tasks")
    
    class Config:
        json_schema_extra = {
            "example": {
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


class SuccessResponse(BaseModel):
    """Generic success response."""
    status: str = Field(default="success", description="Response status")
    message: Optional[str] = Field(None, description="Success message")
    data: Optional[Dict[str, Any]] = Field(None, description="Response data")


class ErrorResponse(BaseModel):
    """Generic error response."""
    status: str = Field(default="error", description="Response status")
    error: Dict[str, Any] = Field(..., description="Error details")
    
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
