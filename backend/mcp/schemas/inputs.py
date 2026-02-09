"""
Input schemas for MCP tools.

Defines Pydantic models for validating tool parameters.
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class AddTaskInput(BaseModel):
    """Input schema for add_task tool."""
    user_id: str = Field(..., min_length=1, max_length=255, description="User identifier")
    title: str = Field(..., min_length=1, max_length=200, description="Task title")
    description: Optional[str] = Field(None, max_length=2000, description="Task description (optional)")
    due_date: Optional[datetime] = Field(None, description="Due date in ISO 8601 format (optional)")


class ListTasksInput(BaseModel):
    """Input schema for list_tasks tool."""
    user_id: str = Field(..., min_length=1, max_length=255, description="User identifier")
    status: Optional[str] = Field("all", description="Filter by status: pending, completed, or all")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user123",
                "status": "pending"
            }
        }


class CompleteTaskInput(BaseModel):
    """Input schema for complete_task tool."""
    user_id: str = Field(..., min_length=1, max_length=255, description="User identifier")
    task_id: int = Field(..., ge=1, description="Task ID to complete")


class DeleteTaskInput(BaseModel):
    """Input schema for delete_task tool."""
    user_id: str = Field(..., min_length=1, max_length=255, description="User identifier")
    task_id: int = Field(..., ge=1, description="Task ID to delete")


class UpdateTaskInput(BaseModel):
    """Input schema for update_task tool."""
    user_id: str = Field(..., min_length=1, max_length=255, description="User identifier")
    task_id: int = Field(..., ge=1, description="Task ID to update")
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="New task title (optional)")
    description: Optional[str] = Field(None, max_length=2000, description="New task description (optional)")
    due_date: Optional[datetime] = Field(None, description="New due date in ISO 8601 format (optional)")
