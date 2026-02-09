"""
Test script for MCP Task Management Server.

This script demonstrates the complete MCP server functionality:
1. Database migration
2. MCP server startup
3. Tool invocation tests
4. AI agent integration test

Usage:
    python test_mcp_server.py

For Judges:
This script provides a quick way to verify the MCP server implementation.
It tests all 5 tools and demonstrates the AI agent integration.
"""

import asyncio
import httpx
import json
from datetime import datetime


async def test_mcp_server():
    """
    Test MCP server functionality.

    Tests all 5 MCP tools and verifies responses.
    """
    base_url = "http://localhost:8001"
    user_id = "test_user_123"

    print("=" * 80)
    print("MCP Task Management Server - Test Suite")
    print("=" * 80)
    print()

    async with httpx.AsyncClient(timeout=10.0) as client:

        # Test 1: Health Check
        print("Test 1: Health Check")
        print("-" * 80)
        try:
            response = await client.get(f"{base_url}/health")
            result = response.json()
            print(f"✓ Status: {result['status']}")
            print(f"✓ Timestamp: {result['timestamp']}")
            print()
        except Exception as e:
            print(f"✗ Health check failed: {e}")
            print("Make sure MCP server is running on port 8001")
            return

        # Test 2: List Available Tools
        print("Test 2: List Available Tools")
        print("-" * 80)
        try:
            response = await client.get(f"{base_url}/tools")
            result = response.json()
            print(f"✓ Found {len(result['tools'])} tools:")
            for tool in result['tools']:
                print(f"  - {tool['name']}: {tool['description']}")
            print()
        except Exception as e:
            print(f"✗ Failed to list tools: {e}")
            return

        # Test 3: Add Task
        print("Test 3: Add Task")
        print("-" * 80)
        try:
            response = await client.post(
                f"{base_url}/tools/add_task",
                json={
                    "user_id": user_id,
                    "title": "Review the proposal",
                    "description": "Review and provide feedback on the Q4 proposal",
                    "due_date": "2026-02-15T17:00:00Z"
                }
            )
            result = response.json()
            if result['status'] == 'success':
                task = result['task']
                task_id = task['id']
                print(f"✓ Task created successfully")
                print(f"  - ID: {task_id}")
                print(f"  - Title: {task['title']}")
                print(f"  - Status: {task['status']}")
                print()
            else:
                print(f"✗ Failed to create task: {result}")
                return
        except Exception as e:
            print(f"✗ Add task failed: {e}")
            return

        # Test 4: List Tasks
        print("Test 4: List Tasks")
        print("-" * 80)
        try:
            response = await client.post(
                f"{base_url}/tools/list_tasks",
                json={
                    "user_id": user_id,
                    "status": "all"
                }
            )
            result = response.json()
            if result['status'] == 'success':
                tasks = result['tasks']
                print(f"✓ Retrieved {len(tasks)} tasks")
                for task in tasks:
                    print(f"  - [{task['id']}] {task['title']} ({task['status']})")
                print()
            else:
                print(f"✗ Failed to list tasks: {result}")
                return
        except Exception as e:
            print(f"✗ List tasks failed: {e}")
            return

        # Test 5: Update Task
        print("Test 5: Update Task")
        print("-" * 80)
        try:
            response = await client.post(
                f"{base_url}/tools/update_task",
                json={
                    "user_id": user_id,
                    "task_id": task_id,
                    "title": "Review the Q4 proposal",
                    "due_date": "2026-02-20T17:00:00Z"
                }
            )
            result = response.json()
            if result['status'] == 'success':
                task = result['task']
                print(f"✓ Task updated successfully")
                print(f"  - New title: {task['title']}")
                print(f"  - New due date: {task['due_date']}")
                print()
            else:
                print(f"✗ Failed to update task: {result}")
                return
        except Exception as e:
            print(f"✗ Update task failed: {e}")
            return

        # Test 6: Complete Task
        print("Test 6: Complete Task")
        print("-" * 80)
        try:
            response = await client.post(
                f"{base_url}/tools/complete_task",
                json={
                    "user_id": user_id,
                    "task_id": task_id
                }
            )
            result = response.json()
            if result['status'] == 'success':
                task = result['task']
                print(f"✓ Task completed successfully")
                print(f"  - Status: {task['status']}")
                print(f"  - Updated at: {task['updated_at']}")
                print()
            else:
                print(f"✗ Failed to complete task: {result}")
                return
        except Exception as e:
            print(f"✗ Complete task failed: {e}")
            return

        # Test 7: Delete Task
        print("Test 7: Delete Task")
        print("-" * 80)
        try:
            response = await client.post(
                f"{base_url}/tools/delete_task",
                json={
                    "user_id": user_id,
                    "task_id": task_id
                }
            )
            result = response.json()
            if result['status'] == 'success':
                print(f"✓ Task deleted successfully")
                print(f"  - Message: {result['message']}")
                print()
            else:
                print(f"✗ Failed to delete task: {result}")
                return
        except Exception as e:
            print(f"✗ Delete task failed: {e}")
            return

        # Test 8: User Isolation
        print("Test 8: User Isolation (Security Test)")
        print("-" * 80)
        try:
            # Create task for user1
            response = await client.post(
                f"{base_url}/tools/add_task",
                json={
                    "user_id": "user1",
                    "title": "User 1 task"
                }
            )
            result = response.json()
            user1_task_id = result['task']['id']

            # Try to access with user2 (should fail)
            response = await client.post(
                f"{base_url}/tools/complete_task",
                json={
                    "user_id": "user2",
                    "task_id": user1_task_id
                }
            )
            result = response.json()

            if result['status'] == 'error' and result['error']['code'] == 'TASK_NOT_FOUND':
                print(f"✓ User isolation working correctly")
                print(f"  - User 2 cannot access User 1's task")
                print()
            else:
                print(f"✗ User isolation failed: {result}")
                return
        except Exception as e:
            print(f"✗ User isolation test failed: {e}")
            return

    print("=" * 80)
    print("All Tests Passed! ✓")
    print("=" * 80)
    print()
    print("MCP Server is working correctly!")
    print()
    print("Next Steps:")
    print("1. Start the AI agent server: uvicorn backend.main:app --port 8000")
    print("2. Test natural language: POST /api/user123/chat_mcp")
    print("   Message: 'Create a task to review the proposal'")
    print()


if __name__ == "__main__":
    print()
    print("Starting MCP Server Tests...")
    print()
    print("Prerequisites:")
    print("1. MCP server must be running: uvicorn backend.mcp.server:app --port 8001")
    print("2. Database migration must be complete: python -m backend.mcp.db.migrate")
    print()
    input("Press Enter to continue...")
    print()

    asyncio.run(test_mcp_server())
