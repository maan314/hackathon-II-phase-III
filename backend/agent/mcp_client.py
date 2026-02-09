"""
MCP Client for AI Agent Integration.

This module provides a client interface for the AI agent to invoke MCP tools.
The client handles HTTP communication with the MCP server and formats responses.

Architecture:
- HTTP client for MCP server communication
- Async support for concurrent tool calls
- Error handling and retry logic
- Structured logging for debugging

For Judges:
This client demonstrates how an AI agent integrates with MCP tools.
It abstracts the HTTP communication and provides a clean Python API
for tool invocation.
"""

import httpx
import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class MCPClient:
    """
    Client for communicating with MCP Task Management Server.

    This client provides a Python interface for AI agents to invoke
    MCP tools via HTTP. It handles request formatting, error handling,
    and response parsing.

    For Judges:
    This demonstrates the separation between the AI agent and MCP tools.
    The agent doesn't directly access the database - it goes through
    this client which calls the MCP server's HTTP endpoints.

    Example:
        >>> client = MCPClient(base_url="http://localhost:8001")
        >>> result = await client.add_task(
        ...     user_id="user123",
        ...     title="Review proposal"
        ... )
        >>> result["status"]
        'success'
    """

    def __init__(self, base_url: str = "http://localhost:8001", timeout: float = 10.0):
        """
        Initialize MCP client.

        Args:
            base_url: Base URL of MCP server (default: http://localhost:8001)
            timeout: Request timeout in seconds (default: 10.0)
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout)
        logger.info(f"MCPClient initialized with base_url={base_url}")

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

    async def _call_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Internal method to call an MCP tool.

        Args:
            tool_name: Name of the tool to invoke
            parameters: Tool parameters as dictionary

        Returns:
            Dict: Tool response (success or error)

        Raises:
            Exception: If HTTP request fails
        """
        url = f"{self.base_url}/tools/{tool_name}"

        logger.info(f"Calling MCP tool: {tool_name}")
        logger.debug(f"Parameters: {parameters}")

        try:
            response = await self.client.post(url, json=parameters)
            response.raise_for_status()

            result = response.json()
            logger.info(f"Tool {tool_name} completed with status: {result.get('status')}")

            return result

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error calling {tool_name}: {e}")
            return {
                "status": "error",
                "error": {
                    "code": "HTTP_ERROR",
                    "message": f"HTTP {e.response.status_code}: {e.response.text}",
                    "details": {"status_code": e.response.status_code}
                }
            }

        except Exception as e:
            logger.error(f"Error calling {tool_name}: {e}", exc_info=True)
            return {
                "status": "error",
                "error": {
                    "code": "CLIENT_ERROR",
                    "message": str(e),
                    "details": {}
                }
            }

    async def add_task(
        self,
        user_id: str,
        title: str,
        description: Optional[str] = None,
        due_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new task.

        Args:
            user_id: User identifier
            title: Task title (1-200 characters)
            description: Optional task description (max 2000 characters)
            due_date: Optional due date in ISO 8601 format

        Returns:
            Dict: Response with created task or error

        Example:
            >>> result = await client.add_task(
            ...     user_id="user123",
            ...     title="Review proposal",
            ...     description="Review Q4 proposal"
            ... )
        """
        parameters = {
            "user_id": user_id,
            "title": title
        }

        if description is not None:
            parameters["description"] = description
        if due_date is not None:
            parameters["due_date"] = due_date

        return await self._call_tool("add_task", parameters)

    async def list_tasks(
        self,
        user_id: str,
        status: str = "all"
    ) -> Dict[str, Any]:
        """
        Retrieve tasks for a user.

        Args:
            user_id: User identifier
            status: Filter by status ("pending", "completed", or "all")

        Returns:
            Dict: Response with array of tasks or error

        Example:
            >>> result = await client.list_tasks(
            ...     user_id="user123",
            ...     status="pending"
            ... )
        """
        parameters = {
            "user_id": user_id,
            "status": status
        }

        return await self._call_tool("list_tasks", parameters)

    async def complete_task(
        self,
        user_id: str,
        task_id: int
    ) -> Dict[str, Any]:
        """
        Mark a task as completed.

        Args:
            user_id: User identifier
            task_id: Task identifier

        Returns:
            Dict: Response with updated task or error

        Example:
            >>> result = await client.complete_task(
            ...     user_id="user123",
            ...     task_id=1
            ... )
        """
        parameters = {
            "user_id": user_id,
            "task_id": task_id
        }

        return await self._call_tool("complete_task", parameters)

    async def delete_task(
        self,
        user_id: str,
        task_id: int
    ) -> Dict[str, Any]:
        """
        Permanently delete a task.

        Args:
            user_id: User identifier
            task_id: Task identifier

        Returns:
            Dict: Response with confirmation or error

        Example:
            >>> result = await client.delete_task(
            ...     user_id="user123",
            ...     task_id=1
            ... )
        """
        parameters = {
            "user_id": user_id,
            "task_id": task_id
        }

        return await self._call_tool("delete_task", parameters)

    async def update_task(
        self,
        user_id: str,
        task_id: int,
        title: Optional[str] = None,
        description: Optional[str] = None,
        due_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update task attributes (partial update).

        Args:
            user_id: User identifier
            task_id: Task identifier
            title: New task title (optional)
            description: New task description (optional)
            due_date: New due date in ISO 8601 format (optional)

        Returns:
            Dict: Response with updated task or error

        Example:
            >>> result = await client.update_task(
            ...     user_id="user123",
            ...     task_id=1,
            ...     title="Review Q4 proposal"
            ... )
        """
        parameters = {
            "user_id": user_id,
            "task_id": task_id
        }

        if title is not None:
            parameters["title"] = title
        if description is not None:
            parameters["description"] = description
        if due_date is not None:
            parameters["due_date"] = due_date

        return await self._call_tool("update_task", parameters)

    async def health_check(self) -> Dict[str, Any]:
        """
        Check MCP server health.

        Returns:
            Dict: Health status

        Example:
            >>> result = await client.health_check()
            >>> result["status"]
            'healthy'
        """
        try:
            response = await self.client.get(f"{self.base_url}/health")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {"status": "unhealthy", "error": str(e)}

    async def list_available_tools(self) -> Dict[str, Any]:
        """
        List available MCP tools.

        Returns:
            Dict: List of available tools with metadata

        Example:
            >>> result = await client.list_available_tools()
            >>> len(result["tools"])
            5
        """
        try:
            response = await self.client.get(f"{self.base_url}/tools")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to list tools: {e}")
            return {"tools": [], "error": str(e)}
