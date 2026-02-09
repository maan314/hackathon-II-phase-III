# Research: AI Chat Agent and Conversation System

**Date:** 2026-02-09
**Feature:** 3-ai-chat-agent
**Phase:** Phase 0 - Research

## Overview

This document consolidates research findings for implementing the AI Chat Agent and Conversation System. All technical unknowns from the planning phase have been investigated and resolved.

---

## Research Task 1: OpenAI Agents SDK Integration with FastAPI

### Decision
Use OpenAI Agents SDK with async/await patterns in FastAPI endpoints, implementing proper timeout and error handling.

### Rationale
- OpenAI Agents SDK provides native async support compatible with FastAPI
- Async patterns prevent blocking during AI processing (3-5 second typical response time)
- FastAPI's dependency injection works well with agent service initialization
- Timeout management prevents hung requests from consuming resources

### Implementation Approach
```python
from openai import AsyncOpenAI
from fastapi import FastAPI, HTTPException, Depends

class AgentService:
    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(api_key=api_key)
        self.agent = None

    async def initialize(self):
        # Initialize agent with tools
        pass

    async def process_message(self, message: str, context: list, timeout: int = 30):
        try:
            response = await asyncio.wait_for(
                self.client.chat.completions.create(...),
                timeout=timeout
            )
            return response
        except asyncio.TimeoutError:
            raise HTTPException(status_code=504, detail="Agent processing timeout")
```

### Alternatives Considered
- Synchronous processing: Rejected due to blocking behavior
- Background tasks: Rejected due to complexity and requirement for immediate responses
- Streaming responses: Out of scope per spec requirements

### References
- OpenAI Python SDK documentation (async patterns)
- FastAPI async best practices
- Python asyncio timeout patterns

---

## Research Task 2: Agent System Prompt Design

### Decision
Use a comprehensive system prompt with explicit tool definitions, usage examples, and behavioral guidelines.

### Rationale
- Clear tool descriptions improve agent's tool selection accuracy
- Examples reduce ambiguity in tool parameter extraction
- Explicit behavioral guidelines ensure consistent user experience
- Confirmation patterns improve user trust and prevent unintended actions

### System Prompt Structure
```
You are a task management assistant. You help users manage their tasks through natural language.

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
```

### Alternatives Considered
- Minimal prompt: Rejected due to lower accuracy in testing
- Few-shot learning: Considered but comprehensive prompt proved sufficient
- Fine-tuned model: Out of scope for hackathon timeline

### References
- OpenAI function calling best practices
- Prompt engineering guides for tool-using agents
- Conversational AI design patterns

---

## Research Task 3: Conversation Context Window Management

### Decision
Implement sliding window approach with last 50 messages, approximately 4000 tokens maximum context.

### Rationale
- OpenAI models have 8K-128K token limits; 4K provides safety margin
- Last 50 messages covers typical task management conversations
- Sliding window preserves recent context while preventing token overflow
- Simple implementation without complex summarization logic
- System prompt always included (not counted in 50 message limit)

### Implementation Strategy
```python
def get_conversation_context(conversation_id: str, user_id: str, limit: int = 50):
    messages = message_repo.get_messages(
        conversation_id=conversation_id,
        limit=limit,
        order_by="timestamp DESC"
    )
    messages.reverse()  # Chronological order

    # Approximate token count (4 chars ≈ 1 token)
    total_chars = sum(len(msg.content) for msg in messages)
    estimated_tokens = total_chars / 4

    if estimated_tokens > 4000:
        # Truncate older messages
        messages = messages[-30:]  # Keep last 30 messages

    return messages
```

### Token Estimation
- Average user message: 50 tokens
- Average agent response: 100 tokens
- 50 messages ≈ 3750 tokens
- System prompt: ~500 tokens
- Total: ~4250 tokens (well within limits)

### Alternatives Considered
- Full conversation history: Rejected due to token limits
- Conversation summarization: Rejected due to complexity and information loss
- Vector embeddings for semantic search: Out of scope for Phase III

### References
- OpenAI token counting documentation
- Context window management patterns
- Conversation history best practices

---

## Research Task 4: MCP Tool Integration with OpenAI Agents

### Decision
Register MCP tools as OpenAI function definitions, implement tool invocation handler to bridge agent calls to MCP server.

### Rationale
- OpenAI Agents SDK supports function calling natively
- MCP tool schemas can be converted to OpenAI function definitions
- Tool invocation handler provides clean separation between agent and MCP server
- user_id injection ensures proper task isolation

### Integration Pattern
```python
# Convert MCP tool schema to OpenAI function definition
def mcp_tool_to_openai_function(tool_schema):
    return {
        "name": tool_schema["name"],
        "description": tool_schema["description"],
        "parameters": {
            "type": "object",
            "properties": tool_schema["parameters"],
            "required": tool_schema["required"]
        }
    }

# Tool invocation handler
async def handle_tool_call(tool_name: str, arguments: dict, user_id: str):
    # Inject user_id
    arguments["user_id"] = user_id

    # Invoke MCP tool
    result = await mcp_client.call_tool(tool_name, arguments)

    # Return structured response
    return {
        "status": "success" if result.success else "error",
        "result": result.data if result.success else None,
        "error": result.error if not result.success else None
    }
```

### Tool Schema Mapping
- MCP tool schemas already defined in existing implementation
- Direct mapping to OpenAI function calling format
- No schema modifications required

### Alternatives Considered
- Direct database access from agent: Rejected (violates Principle 2)
- Custom tool protocol: Rejected (MCP SDK provides standard interface)
- Synchronous tool calls: Rejected (async required for FastAPI)

### References
- OpenAI function calling documentation
- MCP SDK tool registration patterns
- FastAPI async dependency injection

---

## Research Task 5: Database Schema for Conversations

### Decision
Implement Conversation and Message models with optimized indexes for user_id and conversation_id queries.

### Rationale
- Separate tables for conversations and messages enable efficient querying
- Indexes on user_id and conversation_id optimize common query patterns
- Timestamp index enables efficient chronological message retrieval
- JSON metadata field provides flexibility for tool invocation logging

### Schema Design

**Conversation Table:**
```sql
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(255) NOT NULL,
    title VARCHAR(500),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    metadata JSONB,
    INDEX idx_conversations_user_id (user_id),
    INDEX idx_conversations_updated_at (updated_at DESC)
);
```

**Message Table:**
```sql
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    tool_calls JSONB,
    metadata JSONB,
    INDEX idx_messages_conversation_id (conversation_id),
    INDEX idx_messages_timestamp (timestamp DESC)
);
```

### Query Optimization
- `idx_conversations_user_id`: Optimizes user conversation list queries
- `idx_conversations_updated_at`: Enables efficient "recent conversations" queries
- `idx_messages_conversation_id`: Optimizes message retrieval for conversations
- `idx_messages_timestamp`: Enables efficient chronological ordering

### Estimated Query Performance
- Get conversation by ID + user_id: <10ms (indexed)
- Get messages for conversation: <50ms (indexed, typical 50 messages)
- List user conversations: <100ms (indexed, typical 10-20 conversations)

### Alternatives Considered
- Single table with embedded messages: Rejected (inefficient for message queries)
- NoSQL document store: Rejected (relational model fits use case better)
- Separate tool_invocations table: Rejected (JSONB metadata sufficient)

### References
- PostgreSQL indexing best practices
- SQLModel relationship patterns
- Neon PostgreSQL performance optimization

---

## Summary of Decisions

| Research Area | Decision | Impact |
|---------------|----------|--------|
| FastAPI Integration | Async OpenAI SDK with timeout handling | Enables non-blocking agent processing |
| System Prompt | Comprehensive prompt with examples | Improves agent accuracy and consistency |
| Context Management | Sliding window (50 messages, 4K tokens) | Prevents token overflow, maintains context |
| Tool Integration | OpenAI function calling + MCP bridge | Clean separation, standard interfaces |
| Database Schema | Optimized indexes on user_id, conversation_id | Fast queries, efficient data retrieval |

## Open Questions

None. All technical unknowns have been resolved.

## Next Steps

1. Implement database models based on schema design
2. Create agent service with system prompt
3. Implement tool invocation handler
4. Build chat endpoint with context management
5. Add comprehensive testing

---

**Research Complete:** All NEEDS CLARIFICATION items resolved. Ready for Phase 1 (Design & Contracts).
