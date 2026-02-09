"""
CRUD operations for task management.

Provides database operations with user isolation.
"""
from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime

from backend.mcp.db.models import Task, TaskStatus
from backend.mcp.schemas.errors import ToolError, ErrorCodes


def create_task(
    session: Session,
    user_id: str,
    title: str,
    description: Optional[str] = None,
    due_date: Optional[datetime] = None
) -> Task:
    """
    Create a new task for a user.
    
    Args:
        session: Database session
        user_id: User identifier
        title: Task title
        description: Optional task description
        due_date: Optional due date
        
    Returns:
        Created Task instance
        
    Raises:
        ToolError: If database operation fails
    """
    try:
        task = Task(
            user_id=user_id,
            title=title,
            description=description,
            due_date=due_date,
            status=TaskStatus.PENDING
        )
        
        session.add(task)
        session.commit()
        session.refresh(task)
        
        return task
        
    except Exception as e:
        session.rollback()
        raise ToolError(
            code=ErrorCodes.DATABASE_ERROR,
            message=f"Failed to create task: {str(e)}",
            details={"user_id": user_id}
        )


def list_tasks(
    session: Session,
    user_id: str,
    status: Optional[str] = None,
    limit: int = 100
) -> List[Task]:
    """
    List all tasks for a user with optional status filter.
    
    Args:
        session: Database session
        user_id: User identifier
        status: Optional status filter (pending, completed, or all)
        limit: Maximum number of tasks to return
        
    Returns:
        List of Task instances
        
    Raises:
        ToolError: If database operation fails
    """
    try:
        query = select(Task).where(Task.user_id == user_id)
        
        # Apply status filter if provided
        if status and status != "all":
            if status == "pending":
                query = query.where(Task.status == TaskStatus.PENDING)
            elif status == "completed":
                query = query.where(Task.status == TaskStatus.COMPLETED)
        
        # Order by created_at descending and apply limit
        query = query.order_by(Task.created_at.desc()).limit(limit)
        
        tasks = session.exec(query).all()
        return list(tasks)
        
    except Exception as e:
        raise ToolError(
            code=ErrorCodes.DATABASE_ERROR,
            message=f"Failed to list tasks: {str(e)}",
            details={"user_id": user_id}
        )


def get_task(session: Session, user_id: str, task_id: int) -> Optional[Task]:
    """
    Get a specific task with user isolation.
    
    Args:
        session: Database session
        user_id: User identifier
        task_id: Task ID
        
    Returns:
        Task instance if found, None otherwise
    """
    query = select(Task).where(
        Task.id == task_id,
        Task.user_id == user_id
    )
    return session.exec(query).first()


def complete_task(session: Session, user_id: str, task_id: int) -> Task:
    """
    Mark a task as completed.
    
    Args:
        session: Database session
        user_id: User identifier
        task_id: Task ID
        
    Returns:
        Updated Task instance
        
    Raises:
        ToolError: If task not found or database operation fails
    """
    try:
        task = get_task(session, user_id, task_id)
        
        if not task:
            raise ToolError(
                code=ErrorCodes.TASK_NOT_FOUND,
                message=f"Task with id {task_id} not found for user {user_id}",
                details={"task_id": task_id, "user_id": user_id}
            )
        
        task.status = TaskStatus.COMPLETED
        task.updated_at = datetime.utcnow()
        
        session.add(task)
        session.commit()
        session.refresh(task)
        
        return task
        
    except ToolError:
        raise
    except Exception as e:
        session.rollback()
        raise ToolError(
            code=ErrorCodes.DATABASE_ERROR,
            message=f"Failed to complete task: {str(e)}",
            details={"task_id": task_id, "user_id": user_id}
        )


def delete_task(session: Session, user_id: str, task_id: int) -> bool:
    """
    Delete a task permanently.
    
    Args:
        session: Database session
        user_id: User identifier
        task_id: Task ID
        
    Returns:
        True if deleted successfully
        
    Raises:
        ToolError: If task not found or database operation fails
    """
    try:
        task = get_task(session, user_id, task_id)
        
        if not task:
            raise ToolError(
                code=ErrorCodes.TASK_NOT_FOUND,
                message=f"Task with id {task_id} not found for user {user_id}",
                details={"task_id": task_id, "user_id": user_id}
            )
        
        session.delete(task)
        session.commit()
        
        return True
        
    except ToolError:
        raise
    except Exception as e:
        session.rollback()
        raise ToolError(
            code=ErrorCodes.DATABASE_ERROR,
            message=f"Failed to delete task: {str(e)}",
            details={"task_id": task_id, "user_id": user_id}
        )


def update_task(
    session: Session,
    user_id: str,
    task_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
    due_date: Optional[datetime] = None
) -> Task:
    """
    Update task attributes (partial update).
    
    Args:
        session: Database session
        user_id: User identifier
        task_id: Task ID
        title: Optional new title
        description: Optional new description
        due_date: Optional new due date
        
    Returns:
        Updated Task instance
        
    Raises:
        ToolError: If task not found or database operation fails
    """
    try:
        task = get_task(session, user_id, task_id)
        
        if not task:
            raise ToolError(
                code=ErrorCodes.TASK_NOT_FOUND,
                message=f"Task with id {task_id} not found for user {user_id}",
                details={"task_id": task_id, "user_id": user_id}
            )
        
        # Update only provided fields
        if title is not None:
            task.title = title
        if description is not None:
            task.description = description
        if due_date is not None:
            task.due_date = due_date
        
        task.updated_at = datetime.utcnow()
        
        session.add(task)
        session.commit()
        session.refresh(task)
        
        return task
        
    except ToolError:
        raise
    except Exception as e:
        session.rollback()
        raise ToolError(
            code=ErrorCodes.DATABASE_ERROR,
            message=f"Failed to update task: {str(e)}",
            details={"task_id": task_id, "user_id": user_id}
        )
