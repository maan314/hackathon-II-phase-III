"""
AI Agent Service for processing user messages and invoking tools.

Uses Cohere API for natural language understanding and tool calling.
"""
import os
import asyncio
from typing import List, Dict, Optional
from sqlmodel import Session
import cohere


class AgentService:
    """
    Service for AI agent operations using Cohere API.

    Handles message processing, tool invocation, and conversation context management.
    """

    def __init__(self):
        """
        Initialize AgentService with Cohere client and configuration.

        Loads configuration from environment variables:
        - COHERE_API_KEY: Cohere API key
        - AGENT_MODEL: Model to use (default: command-r-plus)
        - AGENT_TEMPERATURE: Temperature for responses (default: 0.7)
        - AGENT_MAX_TOKENS: Maximum tokens in response (default: 1000)
        - AGENT_TIMEOUT: Request timeout in seconds (default: 30)
        - USE_MOCK_AI: Set to "true" to use mock responses for testing (default: false)
        """
        self.use_mock = os.getenv("USE_MOCK_AI", "false").lower() == "true"
        self.client = cohere.AsyncClient(api_key=os.getenv("COHERE_API_KEY")) if not self.use_mock else None
        self.model = os.getenv("AGENT_MODEL", "command-r-08-2024")
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

CURRENT DATE AND TIME:
- Today is February 10, 2026 (2026-02-10)
- When user says "tomorrow", use 2026-02-11
- When user says "next week", use dates in February 2026
- Always use year 2026 for current and future dates
- NEVER use 2024 or 2025 - we are in 2026

CRITICAL BEHAVIOR RULE:
- NEVER say "I will use X tool" or "I will do Y" - just call the tool silently
- DO NOT explain your process or what you're about to do
- Just call the tool and wait for results
- Users want action and results, not explanations of your process

CRITICAL: YOU MUST ALWAYS USE TOOLS - NEVER PRETEND
- When user asks to complete a task, you MUST call complete_task tool
- When user asks to delete a task, you MUST call delete_task tool
- When user asks to update a task, you MUST call update_task tool
- NEVER say you completed/deleted/updated a task without actually calling the tool
- If you don't call the tool, the action DOES NOT HAPPEN in the database

CRITICAL: COMPLETING MULTIPLE TASKS
When user says "mark all tasks as completed" or "complete all tasks":
1. First call list_tasks to get all task IDs
2. Then call complete_task ONCE for EACH task ID
3. You must make multiple complete_task calls - one per task
Example: If there are 4 tasks, you must call complete_task 4 times

CRITICAL: TASK IDs ARE ALWAYS NUMBERS
- When you list tasks, you get task_id as a NUMBER (e.g., 9, 11, 2)
- When completing, updating, or deleting tasks, you MUST use the NUMERIC task_id
- NEVER use the task title (e.g., "Get the milk") as the task_id
- ALWAYS use the number (e.g., "9")

Example:
- list_tasks returns: {"task_id": 9, "title": "Get the milk"}
- To complete it, call: complete_task(task_id="9")  ← Use the NUMBER
- WRONG: complete_task(task_id="Get the milk")  ← NEVER do this

AVAILABLE TOOLS:
1. add_task(title, description, due_date, priority, user_id)
   - Creates a new task
   - Example: "Add a task to buy groceries tomorrow" → add_task(title="Buy groceries", due_date="2026-02-10", user_id=...)

2. list_tasks(status, due_date_filter, user_id)
   - Lists tasks with optional filters
   - Returns tasks with NUMERIC task_id field
   - Example: "What tasks do I have this week?" → list_tasks(due_date_filter="this_week", user_id=...)

3. update_task(task_id, title, description, due_date, priority, user_id)
   - Updates an existing task
   - task_id MUST be a NUMBER from list_tasks response
   - Example: "Change the deadline to Friday" → update_task(task_id="9", due_date="2026-02-14", user_id=...)

4. complete_task(task_id, user_id)
   - Marks a task as completed
   - task_id MUST be a NUMBER from list_tasks response
   - Example: "Mark task 9 as done" → complete_task(task_id="9", user_id=...)

5. reopen_task(task_id, user_id)
   - Marks a completed task as incomplete/pending (reopens it)
   - Use this when user wants to uncomplete or reopen a task
   - task_id MUST be a NUMBER from list_tasks response
   - Example: "Mark task 9 as incomplete" → reopen_task(task_id="9", user_id=...)
   - Example: "Reopen task 9" → reopen_task(task_id="9", user_id=...)
   - Example: "Uncomplete task 9" → reopen_task(task_id="9", user_id=...)

6. delete_task(task_id, user_id)
   - Deletes a task permanently
   - task_id MUST be a NUMBER from list_tasks response
   - Example: "Delete task 9" → delete_task(task_id="9", user_id=...)

BEHAVIORAL GUIDELINES:
- Call tools immediately without announcing what you're about to do
- After tool execution, provide brief, direct confirmations
- When user says "mark them all as complete", first list tasks to get their IDs, then complete each one using the NUMERIC task_id
- Ask clarifying questions when user intent is ambiguous
- Provide friendly, conversational responses
- Reference previous conversation context when relevant
- Handle errors gracefully with helpful suggestions
- When listing tasks, format them clearly with task IDs shown
- For date references like "tomorrow", "next week", calculate the actual date
"""

    def _load_tools(self) -> List[Dict]:
        """
        Load MCP tool schemas and convert to Cohere tool format.

        Returns:
            List of tool definitions in Cohere tool calling format
        """
        # Tool schemas for Cohere tool calling
        return [
            {
                "name": "add_task",
                "description": "Create a new task",
                "parameter_definitions": {
                    "title": {
                        "type": "str",
                        "description": "Task title",
                        "required": True
                    },
                    "description": {
                        "type": "str",
                        "description": "Task description (optional)",
                        "required": False
                    },
                    "due_date": {
                        "type": "str",
                        "description": "Due date in YYYY-MM-DD format (optional)",
                        "required": False
                    },
                    "priority": {
                        "type": "str",
                        "description": "Task priority: low, medium, or high (optional, default: medium)",
                        "required": False
                    }
                }
            },
            {
                "name": "list_tasks",
                "description": "List tasks with optional filters",
                "parameter_definitions": {
                    "status": {
                        "type": "str",
                        "description": "Filter by task status: pending, completed, or all (optional, default: pending)",
                        "required": False
                    },
                    "due_date_filter": {
                        "type": "str",
                        "description": "Filter by due date: today, this_week, overdue, or all (optional)",
                        "required": False
                    }
                }
            },
            {
                "name": "update_task",
                "description": "Update an existing task. IMPORTANT: You must use the numeric task_id (e.g., 9, not 'Get the milk'). Get the task_id from list_tasks first.",
                "parameter_definitions": {
                    "task_id": {
                        "type": "str",
                        "description": "Numeric task ID (e.g., '9', '11'). NOT the task title. Get this from list_tasks response.",
                        "required": True
                    },
                    "title": {
                        "type": "str",
                        "description": "New task title (optional)",
                        "required": False
                    },
                    "description": {
                        "type": "str",
                        "description": "New task description (optional)",
                        "required": False
                    },
                    "due_date": {
                        "type": "str",
                        "description": "New due date in YYYY-MM-DD format (optional)",
                        "required": False
                    },
                    "priority": {
                        "type": "str",
                        "description": "New task priority: low, medium, or high (optional)",
                        "required": False
                    }
                }
            },
            {
                "name": "complete_task",
                "description": "Mark a task as completed. IMPORTANT: You must use the numeric task_id (e.g., 9, not 'Get the milk'). Get the task_id from list_tasks first.",
                "parameter_definitions": {
                    "task_id": {
                        "type": "str",
                        "description": "Numeric task ID (e.g., '9', '11'). NOT the task title. Get this from list_tasks response.",
                        "required": True
                    }
                }
            },
            {
                "name": "reopen_task",
                "description": "Mark a completed task as incomplete/pending (reopen it). IMPORTANT: You must use the numeric task_id (e.g., 9, not 'Get the milk'). Get the task_id from list_tasks first.",
                "parameter_definitions": {
                    "task_id": {
                        "type": "str",
                        "description": "Numeric task ID (e.g., '9', '11'). NOT the task title. Get this from list_tasks response.",
                        "required": True
                    }
                }
            },
            {
                "name": "delete_task",
                "description": "Delete a task permanently. IMPORTANT: You must use the numeric task_id (e.g., 9, not 'Get the milk'). Get the task_id from list_tasks first.",
                "parameter_definitions": {
                    "task_id": {
                        "type": "str",
                        "description": "Numeric task ID (e.g., '9', '11'). NOT the task title. Get this from list_tasks response.",
                        "required": True
                    }
                }
            }
        ]

    def _generate_mock_response(self, user_message: str, user_id: str) -> Dict:
        """
        Generate mock AI response for testing without Cohere API.

        Args:
            user_message: User's message text
            user_id: User identifier

        Returns:
            Dict with content and tool_calls
        """
        import re
        from datetime import datetime, timedelta

        msg_lower = user_message.lower()

        # Pattern matching for task operations
        if any(word in msg_lower for word in ["create", "add", "new task", "make a task"]):
            # Extract task title from message
            title_match = re.search(r'(?:create|add|new task|make a task)(?:\s+(?:a|to))?\s+(.+)', msg_lower)
            title = title_match.group(1) if title_match else "New Task"

            return {
                "content": f"I'll create a task '{title}' for you.",
                "tool_calls": None  # Mock mode doesn't actually call tools
            }

        elif any(word in msg_lower for word in ["list", "show", "what tasks", "my tasks"]):
            return {
                "content": "Here are your tasks:\n1. Review proposal (pending)\n2. Update documentation (pending)\n\n(Mock response - connect valid Cohere API key for real task management)",
                "tool_calls": None
            }

        elif any(word in msg_lower for word in ["complete", "done", "finish", "mark as complete"]):
            return {
                "content": "I've marked the task as completed.",
                "tool_calls": None
            }

        elif any(word in msg_lower for word in ["delete", "remove"]):
            return {
                "content": "I've deleted the task.",
                "tool_calls": None
            }

        elif any(word in msg_lower for word in ["update", "change", "modify"]):
            return {
                "content": "I've updated the task details.",
                "tool_calls": None
            }

        else:
            # General conversational response
            return {
                "content": f"I understand you said: '{user_message}'. I'm running in mock mode for testing. To enable full AI capabilities with task management, please configure a valid Cohere API key in the backend .env file and set USE_MOCK_AI=false.",
                "tool_calls": None
            }

    async def process_message(
        self,
        user_message: str,
        conversation_history: List[Dict],
        user_id: str,
        session: Session = None
    ) -> Dict:
        """
        Process user message with AI agent and return response.

        Uses two-step process with actual tool execution:
        1. First API call: Agent decides which tools to use
        2. Execute tools and get real results
        3. Second API call: Agent generates final response based on actual tool results

        Args:
            user_message: User's message text
            conversation_history: List of previous messages in format [{"role": "user/assistant", "content": "..."}]
            user_id: User identifier for tool invocations
            session: Database session for tool execution

        Returns:
            Dict with keys:
                - content: Agent's response text (final response after tool execution)
                - tool_calls: List of tool invocations (if any)

        Raises:
            Exception: If agent processing fails or times out
        """
        try:
            # Use mock response if enabled
            if self.use_mock:
                return self._generate_mock_response(user_message, user_id)

            # Convert conversation history to Cohere chat_history format
            chat_history = []
            for msg in conversation_history:
                role = "USER" if msg["role"] == "user" else "CHATBOT"
                chat_history.append({
                    "role": role,
                    "message": msg["content"]
                })

            # STEP 1: First API call - Agent decides which tools to use
            response = await asyncio.wait_for(
                self.client.chat(
                    model=self.model,
                    message=user_message,
                    chat_history=chat_history,
                    preamble=self.system_prompt,
                    tools=self.tools,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens
                ),
                timeout=self.timeout
            )

            # Extract tool calls if present
            tool_calls = None
            if hasattr(response, 'tool_calls') and response.tool_calls:
                tool_calls = []
                for tool_call in response.tool_calls:
                    tool_calls.append({
                        "name": tool_call.name,
                        "parameters": tool_call.parameters
                    })

                # STEP 2: Execute tools and get REAL results
                if session:
                    from services.tool_handler import ToolHandler
                    tool_handler = ToolHandler(session)

                    tool_results = []
                    for tc in tool_calls:
                        try:
                            # Execute tool with real database operations
                            result = await tool_handler.invoke_tool(
                                tool_name=tc["name"],
                                arguments=tc["parameters"],
                                user_id=user_id
                            )

                            tool_results.append({
                                "call": {
                                    "name": tc["name"],
                                    "parameters": tc["parameters"]
                                },
                                "outputs": [result]
                            })
                        except Exception as e:
                            tool_results.append({
                                "call": {
                                    "name": tc["name"],
                                    "parameters": tc["parameters"]
                                },
                                "outputs": [{
                                    "status": "error",
                                    "error": str(e)
                                }]
                            })

                    # Add the assistant's tool call message to history
                    # Use empty message to avoid showing "I will..." text
                    chat_history.append({
                        "role": "CHATBOT",
                        "message": "",  # Empty to suppress "I will..." explanations
                        "tool_calls": [
                            {
                                "name": tc["name"],
                                "parameters": tc["parameters"]
                            }
                            for tc in tool_calls
                        ]
                    })

                    # STEP 3: Second API call with ACTUAL tool results
                    final_response = await asyncio.wait_for(
                        self.client.chat(
                            model=self.model,
                            message="",  # Empty message for tool result processing
                            chat_history=chat_history,
                            preamble=self.system_prompt,
                            tools=self.tools,
                            tool_results=tool_results,
                            temperature=self.temperature,
                            max_tokens=self.max_tokens
                        ),
                        timeout=self.timeout
                    )

                    content = final_response.text if hasattr(final_response, 'text') else ""
                else:
                    # No session provided - return placeholder response
                    content = response.text if hasattr(response, 'text') else ""
            else:
                # No tool calls - use the first response
                content = response.text if hasattr(response, 'text') else ""

            return {
                "content": content,
                "tool_calls": tool_calls
            }

        except asyncio.TimeoutError:
            raise Exception("Agent processing timeout - request took too long")
        except Exception as e:
            raise Exception(f"Agent processing error: {str(e)}")
