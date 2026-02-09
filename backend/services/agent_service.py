"""
AI Agent Service for processing user messages and invoking tools.

Uses OpenAI Agents SDK for natural language understanding and tool calling.
"""
import os
import asyncio
from typing import List, Dict, Optional
from openai import AsyncOpenAI


class AgentService:
    """
    Service for AI agent operations using OpenAI Agents SDK.

    Handles message processing, tool invocation, and conversation context management.
    """

    def __init__(self):
        """
        Initialize AgentService with OpenAI client and configuration.

        Loads configuration from environment variables:
        - OPENAI_API_KEY: OpenAI API key
        - AGENT_MODEL: Model to use (default: gpt-4-turbo-preview)
        - AGENT_TEMPERATURE: Temperature for responses (default: 0.7)
        - AGENT_MAX_TOKENS: Maximum tokens in response (default: 1000)
        - AGENT_TIMEOUT: Request timeout in seconds (default: 30)
        """
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = os.getenv("AGENT_MODEL", "gpt-4-turbo-preview")
        self.temperature = float(os.getenv("AGENT_TEMPERATURE", "0.7"))
        self.max_tokens = int(os.getenv("AGENT_MAX_TOKENS", "1000"))
        self.timeout = int(os.getenv("AGENT_TIMEOUT", "30"))
        self.system_prompt = self._load_system_prompt()
        self.tools = self._load_tools()

    def _load_system_prompt(self) -> str:
        """
        Load system prompt for task management agent.

        Returns:
            System prompt string with tool descriptions and behavioral guidelines
        """
        return """You are a task management assistant. You help users manage their tasks through natural language.

AVAILABLE TOOLS:
1. add_task(title, description, due_date, priority, user_id)
   - Creates a new task
   - Example: "Add a task to buy groceries tomorrow" → add_task(title="Buy groceries", due_date="2026-02-10", user_id=...)

2. list_tasks(status, due_date_filter, user_id)
   - Lists tasks with optional filters
   - Example: "What tasks do I have this week?" → list_tasks(due_date_filter="this_week", user_id=...)

3. update_task(task_id, title, description, due_date, priority, user_id)
   - Updates an existing task
   - Example: "Change the deadline to Friday" → update_task(task_id=..., due_date="2026-02-14", user_id=...)

4. complete_task(task_id, user_id)
   - Marks a task as completed
   - Example: "Mark the groceries task as done" → complete_task(task_id=..., user_id=...)

5. delete_task(task_id, user_id)
   - Deletes a task permanently
   - Example: "Delete that task" → delete_task(task_id=..., user_id=...)

BEHAVIORAL GUIDELINES:
- Always confirm actions before executing tools
- Ask clarifying questions when user intent is ambiguous
- Provide friendly, conversational responses
- Reference previous conversation context when relevant
- Handle errors gracefully with helpful suggestions
- When listing tasks, format them clearly with numbers or bullets
- For date references like "tomorrow", "next week", calculate the actual date
"""

    def _load_tools(self) -> List[Dict]:
        """
        Load MCP tool schemas and convert to OpenAI function format.

        Returns:
            List of tool definitions in OpenAI function calling format
        """
        # Tool schemas for OpenAI function calling
        return [
            {
                "type": "function",
                "function": {
                    "name": "add_task",
                    "description": "Create a new task",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "Task title"
                            },
                            "description": {
                                "type": "string",
                                "description": "Task description (optional)"
                            },
                            "due_date": {
                                "type": "string",
                                "description": "Due date in YYYY-MM-DD format (optional)"
                            },
                            "priority": {
                                "type": "string",
                                "enum": ["low", "medium", "high"],
                                "description": "Task priority (optional, default: medium)"
                            }
                        },
                        "required": ["title"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "list_tasks",
                    "description": "List tasks with optional filters",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "status": {
                                "type": "string",
                                "enum": ["pending", "completed", "all"],
                                "description": "Filter by task status (optional, default: pending)"
                            },
                            "due_date_filter": {
                                "type": "string",
                                "enum": ["today", "this_week", "overdue", "all"],
                                "description": "Filter by due date (optional)"
                            }
                        },
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "update_task",
                    "description": "Update an existing task",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "string",
                                "description": "Task ID to update"
                            },
                            "title": {
                                "type": "string",
                                "description": "New task title (optional)"
                            },
                            "description": {
                                "type": "string",
                                "description": "New task description (optional)"
                            },
                            "due_date": {
                                "type": "string",
                                "description": "New due date in YYYY-MM-DD format (optional)"
                            },
                            "priority": {
                                "type": "string",
                                "enum": ["low", "medium", "high"],
                                "description": "New task priority (optional)"
                            }
                        },
                        "required": ["task_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "complete_task",
                    "description": "Mark a task as completed",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "string",
                                "description": "Task ID to complete"
                            }
                        },
                        "required": ["task_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "delete_task",
                    "description": "Delete a task permanently",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "string",
                                "description": "Task ID to delete"
                            }
                        },
                        "required": ["task_id"]
                    }
                }
            }
        ]

    async def process_message(
        self,
        user_message: str,
        conversation_history: List[Dict],
        user_id: str
    ) -> Dict:
        """
        Process user message with AI agent and return response.

        Args:
            user_message: User's message text
            conversation_history: List of previous messages in format [{"role": "user/assistant", "content": "..."}]
            user_id: User identifier for tool invocations

        Returns:
            Dict with keys:
                - content: Agent's response text
                - tool_calls: List of tool invocations (if any)

        Raises:
            Exception: If agent processing fails or times out
        """
        try:
            # Build messages array with system prompt, history, and current message
            messages = [{"role": "system", "content": self.system_prompt}]
            messages.extend(conversation_history)
            messages.append({"role": "user", "content": user_message})

            # Call OpenAI API with timeout
            response = await asyncio.wait_for(
                self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    tools=self.tools,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens
                ),
                timeout=self.timeout
            )

            # Extract response
            message = response.choices[0].message

            return {
                "content": message.content or "",
                "tool_calls": message.tool_calls if message.tool_calls else None
            }

        except asyncio.TimeoutError:
            raise Exception("Agent processing timeout - request took too long")
        except Exception as e:
            raise Exception(f"Agent processing error: {str(e)}")
