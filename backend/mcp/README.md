# MCP Task Tooling Server

Model Context Protocol (MCP) server providing task management tools for AI agents.

## Features

- **5 Task Management Tools:**
  - `add_task` - Create new tasks
  - `list_tasks` - Retrieve tasks with filtering
  - `complete_task` - Mark tasks as completed
  - `delete_task` - Remove tasks permanently
  - `update_task` - Modify task attributes

- **Stateless Architecture:** No in-memory state, all data persisted in PostgreSQL
- **User Isolation:** Strict user_id filtering on all operations
- **Schema Validation:** Pydantic-based input/output validation
- **Structured Logging:** JSON-formatted logs with request tracing
- **Error Handling:** Consistent error response format

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL database (Neon recommended)
- Environment variables configured

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
cp backend/mcp/.env.example backend/mcp/.env
# Edit .env with your DATABASE_URL
```

### Database Setup

```bash
# Run migrations
python -m backend.mcp.db.migrate

# Seed test data (optional)
python -m backend.mcp.db.seed
```

### Start Server

```bash
# Development mode (with auto-reload)
python backend/mcp/server.py

# Or with uvicorn
uvicorn backend.mcp.server:app --host 0.0.0.0 --port 8001 --reload
```

Server will start on http://localhost:8001

## API Endpoints

### Health Check
```bash
GET /health
```

### List Tools
```bash
GET /tools
```

### Tool Invocations

All tools accept POST requests with JSON body:

**Add Task:**
```bash
POST /tools/add_task
{
  "user_id": "user123",
  "title": "Review proposal",
  "description": "Review Q4 proposal",
  "due_date": "2026-02-15T17:00:00Z"
}
```

**List Tasks:**
```bash
POST /tools/list_tasks
{
  "user_id": "user123",
  "status": "pending"
}
```

**Complete Task:**
```bash
POST /tools/complete_task
{
  "user_id": "user123",
  "task_id": 1
}
```

**Delete Task:**
```bash
POST /tools/delete_task
{
  "user_id": "user123",
  "task_id": 1
}
```

**Update Task:**
```bash
POST /tools/update_task
{
  "user_id": "user123",
  "task_id": 1,
  "title": "Updated title",
  "due_date": "2026-02-20T17:00:00Z"
}
```

## Architecture

```
backend/mcp/
├── server.py           # FastAPI application
├── config.py           # Configuration management
├── logging_config.py   # Structured logging
├── db/
│   ├── models.py       # SQLModel entities
│   ├── engine.py       # Database engine
│   ├── crud.py         # CRUD operations
│   ├── migrate.py      # Migration runner
│   └── migrations/     # SQL migration scripts
├── schemas/
│   ├── inputs.py       # Input validation schemas
│   ├── outputs.py      # Output response schemas
│   └── errors.py       # Error handling
└── tools/
    ├── add_task.py     # Add task tool handler
    ├── list_tasks.py   # List tasks tool handler
    ├── complete_task.py    # Complete task tool handler
    ├── delete_task.py  # Delete task tool handler
    └── update_task.py  # Update task tool handler
```

## Configuration

Environment variables (`.env`):

```env
DATABASE_URL=postgresql://user:password@host.neon.tech/dbname?sslmode=require
MCP_SERVER_PORT=8001
MCP_SERVER_HOST=0.0.0.0
ENVIRONMENT=development
LOG_LEVEL=INFO
```

## Testing

```bash
# Test health check
curl http://localhost:8001/health

# Test tool invocation
curl -X POST http://localhost:8001/tools/add_task \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user123", "title": "Test task"}'
```

## Integration with AI Agent

The MCP server is designed to be called by the AI Chat Agent (port 8000). The agent extracts user_id from JWT tokens and passes it to all tool invocations.

## Production Deployment

```bash
# Run with multiple workers
uvicorn backend.mcp.server:app --host 0.0.0.0 --port 8001 --workers 4

# Or use gunicorn
gunicorn backend.mcp.server:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8001
```

## Troubleshooting

**Database connection issues:**
- Verify DATABASE_URL is correct
- Check Neon project is active
- Ensure SSL mode is set: `?sslmode=require`

**Tool invocation errors:**
- Check server logs for detailed error messages
- Verify input parameters match schema requirements
- Ensure database migration has been run

## Documentation

- API Documentation: http://localhost:8001/docs
- ReDoc: http://localhost:8001/redoc
- Specification: `specs/3-mcp-task-tools/spec.md`
- Implementation Plan: `specs/3-mcp-task-tools/plan.md`
