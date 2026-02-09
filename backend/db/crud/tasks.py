"""
CRUD operations for Task model.

All operations enforce user isolation through user_id filtering.
Stateless design - no in-memory caching, fresh queries per request.

MCP Tool Integration:
- These functions are called exclusively by MCP tool handlers
- All operations validate user ownership before mutations
- Errors are raised as exceptions for tool handlers to format
"""

from sqlmodel import Session, select
from datetime import datetime
from typing import List, Optional
from fastapi import HTTPException

from backend.db.models import Task, TaskStatus


def create_task(
    session: Session,
    user_id: str,
    title: str,
    description: Optional[str] = None,
    due_date: Optional[datetime] = None
) -> Task:
    """
    Create a new task for a user.

    Stateless Design:
    - Task immediately persisted to database
    - No in-memory state maintained

    User Isolation:
    - Task associated with user_id
    - Only this user can access this task

    Args:
        session: Database session
        user_id: User identifier (enforces user isolation)
        title: Task title (1-200 characters)
        description: Optional task description (max 2000 characters)
        due_date: Optional due date

    Returns:
        Task: Newly created task with generated id

    Raises:
        Exception: Database errors
    """
    task = Task(
        user_id=user_id,
        title=title,
        description=description,
        due_date=due_date,
        status=TaskStatus.PENDING,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    session.add(task)
    session.commit()
    session.refresh(task)

    return task


def get_task(session: Session, task_id: int, user_id: str) -> Task:
    """
    Get a specific task by ID with user isolation.

    User Isolation:
    - MUST filter by both task_id AND user_id
    - Prevents users from accessing other users' tasks
    - Returns 404 if task not found OR belongs to different user

    Stateless Design:
    - Fresh query from database per request
    - No caching or in-memory storage

    Args:
        session: Database session
        task_id: Task identifier
        user_id: User identifier (enforces user isolation)

    Returns:
        Task: The requested task

    Raises:
        HTTPException: 404 if task not found or user doesn't have access
    """
    statement = select(Task).where(
        Task.id == task_id,
        Task.user_id == user_id  # User isolation enforcement
    )

    task = session.exec(statement).first()

    if not task:
        raise HTTPException(
            status_code=404,
            detail=f"Task with id {task_id} not found for user {user_id}"
        )

    return task


def list_tasks(
    session: Session,
    user_id: str,
    status: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
) -> List[Task]:
    """
    List tasks for a user with optional status filter.

    User Isolation:
    - MUST filter by user_id
    - Only returns tasks owned by the user

    Stateless Design:
    - Fresh query from database per request
    - No caching of task lists

    Query Optimization:
    - Uses composite index (user_id, status) for filtered queries
    - Uses composite index (user_id, created_at) for ordering
    - Limit prevents large result sets

    Args:
        session: Database session
        user_id: User identifier (enforces user isolation)
        status: Optional status filter ("pending", "completed", or "all")
        limit: Maximum number of tasks to return (default 100)
        offset: Number of tasks to skip for pagination (default 0)

    Returns:
        List[Task]: User's tasks ordered by created_at DESC
    """
    statement = select(Task).where(Task.user_id == user_id)  # User isolation

    # Apply status filter if provided and not "all"
    if status and status != "all":
        try:
            status_enum = TaskStatus(status)
            statement = statement.where(Task.status == status_enum)
        except ValueError:
            # Invalid status value, ignore filter
            pass

    # Order by created_at DESC (most recent first)
    statement = statement.order_by(Task.created_at.desc())

    # Apply pagination
    statement = statement.limit(limit).offset(offset)

    tasks = session.exec(statement).all()

    return list(tasks)


def update_task(
    session: Session,
    task_id: int,
    user_id: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
    due_date: Optional[datetime] = None
) -> Task:
    """
    Update task attributes (partial update).

    User Isolation:
    - Verifies user owns the task before update
    - Prevents users from updating other users' tasks

    Partial Update:
    - Only updates provided fields
    - None values are ignored (not set to NULL)
    - updated_at automatically updated by database trigger

    Args:
        session: Database session
        task_id: Task identifier
        user_id: User identifier (enforces user isolation)
        title: New title (optional)
        description: New description (optional)
        due_date: New due date (optional)

    Returns:
        Task: Updated task

    Raises:
        HTTPException: 404 if task not found or user doesn't have access
    """
    # Get task with user isolation check
    task = get_task(session, task_id, user_id)

    # Update only provided fields
    if title is not None:
        task.title = title
    if description is not None:
        task.description = description
    if due_date is not None:
        task.due_date = due_date

    # updated_at will be automatically updated by database trigger
    session.add(task)
    session.commit()
    session.refresh(task)

    return task


def complete_task(session: Session, task_id: int, user_id: str) -> Task:
    """
    Mark a task as completed.

    User Isolation:
    - Verifies user owns the task before completion
    - Prevents users from completing other users' tasks

    Idempotent:
    - Completing an already completed task is safe
    - Returns the task in completed state

    Args:
        session: Database session
        task_id: Task identifier
        user_id: User identifier (enforces user isolation)

    Returns:
        Task: Completed task

    Raises:
        HTTPException: 404 if task not found or user doesn't have access
    """
    # Get task with user isolation check
    task = get_task(session, task_id, user_id)

    # Update status to completed
    task.status = TaskStatus.COMPLETED
    # updated_at will be automatically updated by database trigger

    session.add(task)
    session.commit()
    session.refresh(task)

    return task


def delete_task(session: Session, task_id: int, user_id: str) -> bool:
    """
    Permanently delete a task.

    User Isolation:
    - Verifies user owns the task before deletion
    - Prevents users from deleting other users' tasks

    Permanent Deletion:
    - Task is permanently removed from database
    - No soft delete or archival (hackathon scope)

    Args:
        session: Database session
        task_id: Task identifier
        user_id: User identifier (enforces user isolation)

    Returns:
        bool: True if deleted successfully

    Raises:
        HTTPException: 404 if task not found or user doesn't have access
    """
    # Get task with user isolation check
    task = get_task(session, task_id, user_id)

    # Permanently delete task
    session.delete(task)
    session.commit()

    return True
