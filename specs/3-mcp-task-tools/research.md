# Research Findings: MCP Server and Task Tooling System

**Date:** 2026-02-09
**Feature:** 3-mcp-task-tools
**Purpose:** Resolve technical clarifications and document architectural decisions

## Research Task 1: MCP SDK Integration Patterns

### Decision: Use Official MCP SDK with FastAPI Integration

**Findings:**
- MCP SDK provides Python library for building MCP servers
- Supports tool registration with JSON schema definitions
- Provides HTTP transport layer for tool invocations
- Includes built-in validation and error handling

**Implementation Approach:**
```python
from mcp import MCPServer, Tool
from fastapi import FastAPI

# Initialize MCP server
mcp_server = MCPServer()

# Register tool with schema
@mcp_server.tool(
    name="add_task",
    description="Create a new task",
    input_schema={
        "type": "object",
        "required": ["user_id", "title"],
        "properties": {
            "user_id": {"type": "string"},
            "title": {"type": "string"}
        }
    }
)
async def add_task(user_id: str, title: str, **kwargs):
    # Tool implementation
    pass

# Integrate with FastAPI
app = FastAPI()
app.include_router(mcp_server.router)
```

**Tool Registration:**
- Tools defined as Python async functions
- Decorated with @mcp_server.tool()
- JSON schemas defined in decorator
- Automatic parameter validation

**HTTP Transport:**
- MCP SDK provides FastAPI router
- Tools exposed at /tools/{tool_name}
- POST requests with JSON body
- Standard HTTP status codes

**Error Handling:**
- Raise MCPError for tool-specific errors
- SDK formats errors consistently
- Validation errors handled automatically

## Research Task 2: Tool Naming Conventions and Versioning

### Decision: snake_case naming without version prefix

**Rationale:**
- Python convention is snake_case
- Hackathon scope doesn't require versioning
- Simple names improve readability
- Easy to add versioning later if needed

**Tool Names:**
- add_task (not addTask or add_task_v1)
- list_tasks
- complete_task
- delete_task
- update_task

**Versioning Strategy (Future):**
- Breaking changes: add_task_v2
- Minor changes: update existing tool (backward compatible)
- Document version in tool description
- Use semantic versioning if multiple versions coexist

**Tool Descriptions:**
- Clear, concise description of what tool does
- Include parameter descriptions
- Specify return value format
- Document error conditions

## Research Task 3: Error Response Format Standardization

### Decision: Consistent error structure with status, code, message, details

**Error Response Format:**
```json
{
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
```

**Error Codes:**
- `VALIDATION_ERROR`: Input validation failed (400)
- `TASK_NOT_FOUND`: Task doesn't exist or no access (404)
- `DATABASE_ERROR`: Database operation failed (500)
- `INTERNAL_ERROR`: Unexpected error (500)

**Error Messages:**
- Human-readable description
- Include relevant identifiers (task_id, user_id)
- Don't leak internal details (stack traces, SQL queries)
- Provide actionable guidance when possible

**Error Details:**
- Optional object with additional context
- Include field names for validation errors
- Include identifiers for not-found errors
- Omit for internal errors (security)

**Implementation:**
```python
class ToolError(Exception):
    def __init__(self, code: str, message: str, details: dict = None):
        self.code = code
        self.message = message
        self.details = details or {}

def format_error_response(error: ToolError):
    return {
        "status": "error",
        "error": {
            "code": error.code,
            "message": error.message,
            "details": error.details
        }
    }
```

## Research Task 4: Transaction Strategy for Neon DB

### Decision: SQLModel session with automatic transaction management

**Transaction Pattern:**
```python
from sqlmodel import Session, create_engine

engine = create_engine(DATABASE_URL, pool_size=10, max_overflow=20)

def add_task_handler(user_id: str, title: str, **kwargs):
    with Session(engine) as session:
        # All operations in this block are transactional
        task = Task(
            user_id=user_id,
            title=title,
            description=kwargs.get('description'),
            due_date=kwargs.get('due_date'),
            status='pending'
        )
        session.add(task)
        session.commit()  # Commit on success
        session.refresh(task)  # Reload from DB
        return task
    # Automatic rollback on exception
```

**Transaction Isolation:**
- Use default isolation level (READ COMMITTED)
- Sufficient for hackathon scope
- Prevents dirty reads
- Allows concurrent reads

**Connection Pooling:**
- pool_size=10: Number of persistent connections
- max_overflow=20: Additional connections when pool exhausted
- pool_timeout=30: Wait time for connection
- pool_recycle=3600: Recycle connections after 1 hour

**Error Handling:**
- Catch database exceptions
- Rollback happens automatically on exception
- Return generic error message (don't leak SQL details)
- Log full error for debugging

**Best Practices:**
- Keep transactions short
- Don't hold connections during external API calls
- Use context manager for automatic cleanup
- Test transaction rollback scenarios

## Research Task 5: Logging and Observability Design

### Decision: Structured JSON logging with tool invocation metrics

**Log Format:**
```json
{
  "timestamp": "2026-02-09T10:30:00.123Z",
  "level": "INFO",
  "logger": "mcp.tools",
  "tool_name": "add_task",
  "user_id": "user123",
  "parameters": {
    "title": "Test task",
    "description": null
  },
  "result": "success",
  "duration_ms": 45,
  "task_id": 456,
  "request_id": "req_abc123"
}
```

**Log Levels:**
- **DEBUG**: Detailed execution flow, SQL queries
- **INFO**: Tool invocations, successful operations
- **WARNING**: Validation failures, not-found errors
- **ERROR**: Database errors, unexpected exceptions

**Logging Implementation:**
```python
import logging
import json
from datetime import datetime

logger = logging.getLogger("mcp.tools")

def log_tool_invocation(tool_name, user_id, parameters, result, duration_ms, **kwargs):
    log_entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "level": "INFO",
        "logger": "mcp.tools",
        "tool_name": tool_name,
        "user_id": user_id,
        "parameters": parameters,
        "result": result,
        "duration_ms": duration_ms,
        **kwargs
    }
    logger.info(json.dumps(log_entry))
```

**Metrics to Collect:**
- Tool invocation counts (by tool_name)
- Tool execution latencies (p50, p95, p99)
- Error rates (by error_code)
- Database query times
- Concurrent tool invocations

**Observability Tools:**
- Structured logs → Log aggregation (e.g., ELK, Datadog)
- Metrics → Time-series database (e.g., Prometheus)
- Traces → Distributed tracing (e.g., Jaeger) - future enhancement

**What to Log:**
- Every tool invocation (start and end)
- All errors with full context
- Validation failures with field details
- Database query times
- User isolation violations (security)

**What NOT to Log:**
- Sensitive data (passwords, tokens)
- Full stack traces in production (log separately)
- Large payloads (truncate if needed)
- PII without proper handling

## Best Practices Summary

### MCP SDK
- Use official SDK for standard compliance
- Register tools with clear descriptions
- Define comprehensive JSON schemas
- Handle errors with MCPError

### Database Design
- Use SQLModel for type-safe ORM
- Implement connection pooling
- Use transactions for consistency
- Add indexes on user_id and created_at

### API Design
- Follow MCP protocol conventions
- Return consistent response format
- Use standard HTTP status codes
- Include request_id for tracing

### Security
- Validate all inputs with schemas
- Filter all queries by user_id
- Use parameterized queries
- Sanitize error messages

### Performance
- Use connection pooling
- Add database indexes
- Keep transactions short
- Monitor query performance

### Error Handling
- Use consistent error format
- Provide actionable error messages
- Log errors with full context
- Don't leak internal details

## Technology Stack Confirmation

**MCP Framework:** Official MCP SDK (Python)
- Tool registration and validation
- HTTP transport layer
- Error handling conventions

**Backend Framework:** FastAPI
- Async support for concurrent requests
- Automatic OpenAPI documentation
- Easy integration with MCP SDK

**ORM:** SQLModel
- Type-safe database operations
- Pydantic validation built-in
- SQLAlchemy under the hood

**Database:** Neon PostgreSQL
- Serverless Postgres (auto-scaling)
- Connection pooling built-in
- TLS encryption by default

**Validation:** Pydantic (via SQLModel)
- JSON schema validation
- Type coercion and validation
- Clear error messages

## Implementation Readiness

All research tasks completed. Key decisions documented:
- ✅ MCP SDK integration pattern defined
- ✅ Tool naming conventions chosen (snake_case, no versioning)
- ✅ Error response format standardized
- ✅ Transaction strategy finalized (SQLModel sessions)
- ✅ Logging and observability design established

**Ready to proceed to Phase 1: Design & Contracts**
