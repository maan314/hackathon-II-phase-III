"""
Tool invocation handler for task operations.

Integrates AI agent with existing task CRUD operations.
"""
from typing import Dict, Any, Optional
from datetime import datetime
from sqlmodel import Session
import logging

from backend.db.crud.tasks import (
    create_task,
    list_tasks,
    update_task,
    complete_task,
    delete_task,
    get_task
)

logger = logging.getLogger(__name__)


class ToolHandler:
    """
    Handles tool invocation from AI agent to task CRUD operations.

    Integrates with existing backend.db.crud.tasks operations.
    """

    def __init__(self, session: Session):
        """
        Initialize tool handler with database session.

        Args:
            session: Database session for task operations
        """
        self.session = session

    async def invoke_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        user_id: str
    ) -> Dict[str, Any]:
        """
        Invoke a tool with user_id injection.

        Args:
            tool_name: Name of the tool to invoke
            arguments: Tool arguments from agent
            user_id: User identifier to inject

        Returns:
            Dict with keys:
                - status: "success" or "error"
                - result: Tool result data (if successful)
                - error: Error message (if failed)
        """
        try:
            logger.info(f"Invoking tool: {tool_name} for user: {user_id}")

            # Route to appropriate tool handler
            if tool_name == "add_task":
                result = await self._handle_add_task(arguments, user_id)
            elif tool_name == "list_tasks":
                result = await self._handle_list_tasks(arguments, user_id)
            elif tool_name == "update_task":
                result = await self._handle_update_task(arguments, user_id)
            elif tool_name == "complete_task":
                result = await self._handle_complete_task(arguments, user_id)
            elif tool_name == "delete_task":
                result = await self._handle_delete_task(arguments, user_id)
            else:
                raise ValueError(f"Unknown tool: {tool_name}")

            return {
                "status": "success",
                "result": result,
                "error": None
            }

        except Exception as e:
            logger.error(f"Tool invocation failed: {tool_name} - {str(e)}")
            return {
                "status": "error",
                "result": None,
                "error": str(e)
            }

    async def _handle_add_task(self, arguments: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Handle add_task tool invocation."""
        title = arguments.get("title")
        description = arguments.get("description")
        due_date_str = arguments.get("due_date")

        # Parse due_date if provided
        due_date = None
        if due_date_str:
            try:
                due_date = datetime.fromisoformat(due_date_str)
            except ValueError:
                # If parsing fails, leave as None
                pass

        # Call existing CRUD operation
        task = create_task(
            session=self.session,
            user_id=user_id,
            title=title,
            description=description,
            due_date=due_date
        )

        return {
            "task_id": task.id,
            "title": task.title,
            "description": task.description,
            "status": task.status.value,
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "created_at": task.created_at.isoformat()
        }

    async def _handle_list_tasks(self, arguments: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Handle list_tasks tool invocation."""
        status_filter = arguments.get("status", "pending")

        # Call existing CRUD operation
        tasks = list_tasks(
            session=self.session,
            user_id=user_id,
            status=status_filter,
            limit=100
        )

        return {
            "tasks": [
                {
                    "task_id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "status": task.status.value,
                    "due_date": task.due_date.isoformat() if task.due_date else None,
                    "created_at": task.created_at.isoformat()
                }
                for task in tasks
            ],
            "count": len(tasks)
        }

    async def _handle_update_task(self, arguments: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Handle update_task tool invocation."""
        task_id = int(arguments.get("task_id"))
        title = arguments.get("title")
        description = arguments.get("description")
        due_date_str = arguments.get("due_date")

        # Parse due_date if provided
        due_date = None
        if due_date_str:
            try:
                due_date = datetime.fromisoformat(due_date_str)
            except ValueError:
                pass

        # Call existing CRUD operation
        task = update_task(
            session=self.session,
            task_id=task_id,
            user_id=user_id,
            title=title,
            description=description,
            due_date=due_date
        )

        return {
            "task_id": task.id,
            "title": task.title,
            "updated": True,
            "message": "Task updated successfully"
        }

    async def _handle_complete_task(self, arguments: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Handle complete_task tool invocation."""
        task_id = int(arguments.get("task_id"))

        # Call existing CRUD operation
        task = complete_task(
            session=self.session,
            task_id=task_id,
            user_id=user_id
        )

        return {
            "task_id": task.id,
            "status": task.status.value,
            "message": "Task marked as completed"
        }

    async def _handle_delete_task(self, arguments: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Handle delete_task tool invocation."""
        task_id = int(arguments.get("task_id"))

        # Call existing CRUD operation
        delete_task(
            session=self.session,
            task_id=task_id,
            user_id=user_id
        )

        return {
            "task_id": task_id,
            "deleted": True,
            "message": "Task deleted successfully"
        }

    def format_tool_result_for_agent(
        self,
        tool_name: str,
        result: Dict[str, Any]
    ) -> str:
        """
        Format tool result for agent consumption.

        Args:
            tool_name: Tool that was invoked
            result: Tool result data

        Returns:
            Formatted string for agent
        """
        if result["status"] == "error":
            return f"Tool execution failed: {result['error']}"

        # Format based on tool type
        data = result["result"]

        if tool_name == "add_task":
            return f"Task created successfully with ID: {data.get('task_id')}"

        elif tool_name == "list_tasks":
            tasks = data.get("tasks", [])
            if not tasks:
                return "No tasks found"
            task_list = "\n".join([
                f"- {t.get('title')} (ID: {t.get('task_id')}, Status: {t.get('status')})"
                for t in tasks
            ])
            return f"Found {len(tasks)} task(s):\n{task_list}"

        elif tool_name == "update_task":
            return f"Task {data.get('task_id')} updated successfully"

        elif tool_name == "complete_task":
            return f"Task {data.get('task_id')} marked as completed"

        elif tool_name == "delete_task":
            return f"Task {data.get('task_id')} deleted successfully"

        return str(data)
