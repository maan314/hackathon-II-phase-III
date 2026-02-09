# Quickstart Guide: MCP Server and Task Tooling System

**Feature:** 3-mcp-task-tools
**Purpose:** Setup and run the MCP server locally

## Prerequisites

### Required Software
- **Python:** 3.11 or higher
- **PostgreSQL Client:** psql (for database verification)
- **Git:** For cloning and version control

### Required Services
- **Neon PostgreSQL:** Database URL with credentials
- **MCP SDK:** Official MCP SDK for Python

### Development Tools (Recommended)
- **VS Code** or **PyCharm** for Python development
- **Postman** or **curl** for API testing
- **pgAdmin** or **DBeaver** for database inspection

## Environment Setup

### 1. Clone Repository

```bash
git clone <repository-url>
cd hackathon-II-phase-III
git checkout 3-mcp-task-tools
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
# Install core dependencies
pip install fastapi uvicorn sqlmodel psycopg2-binary python-dotenv mcp-sdk

# Install development dependencies (optional)
pip install pytest pytest-asyncio httpx black flake8
```

**Dependencies Explained:**
- `fastapi`: Web framework for HTTP endpoints
- `uvicorn`: ASGI server for running FastAPI
- `sqlmodel`: ORM for database operations
- `psycopg2-binary`: PostgreSQL adapter
- `python-dotenv`: Environment variable management
- `mcp-sdk`: Official MCP SDK for tool registration

### 4. Configure Environment Variables

Create `.env` file in project root:

```bash
# Database Configuration
DATABASE_URL=postgresql://user:password@host.neon.tech/dbname?sslmode=require

# MCP Server Configuration
MCP_SERVER_PORT=8001
MCP_SERVER_HOST=0.0.0.0

# Application Configuration
ENVIRONMENT=development
LOG_LEVEL=INFO
```

**Getting Credentials:**

**Neon PostgreSQL:**
1. Sign up at https://neon.tech
2. Create new project
3. Copy connection string from dashboard
4. Format: `postgresql://user:password@host.neon.tech/dbname?sslmode=require`

### 5. Verify Environment

```bash
# Test database connection
python -c "from sqlmodel import create_engine; engine = create_engine('$DATABASE_URL'); print('Database connected!')"

# Test MCP SDK import
python -c "from mcp import MCPServer; print('MCP SDK available!')"
```

## Database Setup

### 1. Run Database Migration

```bash
# Navigate to backend directory
cd backend/mcp

# Run migration script
python -m db.migrate

# Expected output:
# Creating tasks table...
# Creating indexes...
# Creating triggers...
# Migration completed successfully!
```

**Migration Script Location:** `backend/mcp/db/migrate.py`

**What It Does:**
- Creates `tasks` table with all columns
- Adds indexes for performance (user_id, created_at, composite)
- Creates trigger for auto-updating updated_at
- Validates schema

### 2. Verify Database Schema

```bash
# Connect to database
psql $DATABASE_URL

# List tables
\dt

# Expected output:
# tasks

# Describe tasks table
\d tasks

# Expected columns:
# id, user_id, title, description, status, due_date, created_at, updated_at

# List indexes
\di

# Expected indexes:
# idx_tasks_user_id
# idx_tasks_created_at
# idx_tasks_user_status
# idx_tasks_user_created

# Exit psql
\q
```

### 3. Seed Test Data (Optional)

```bash
# Run seed script
python -m db.seed

# Creates:
# - 2 test users (user123, user456)
# - 5 tasks per user
# - Mix of pending and completed tasks
```

## Running the MCP Server

### 1. Start Development Server

```bash
# From project root
uvicorn backend.mcp.server:app --reload --host 0.0.0.0 --port 8001

# Expected output:
# INFO:     Uvicorn running on http://0.0.0.0:8001 (Press CTRL+C to quit)
# INFO:     Started reloader process
# INFO:     Started server process
# INFO:     Application startup complete.
# INFO:     MCP Server initialized with 5 tools
```

**Server Options:**
- `--reload`: Auto-reload on code changes (development only)
- `--host 0.0.0.0`: Accept connections from any IP
- `--port 8001`: Listen on port 8001
- `--workers 4`: Run with 4 worker processes (production)

### 2. Verify Server is Running

```bash
# Health check endpoint
curl http://localhost:8001/health

# Expected response:
# {"status": "healthy", "timestamp": "2026-02-09T10:30:00Z"}

# List available tools
curl http://localhost:8001/tools

# Expected response:
# {
#   "tools": [
#     {"name": "add_task", "description": "Create a new task"},
#     {"name": "list_tasks", "description": "Retrieve all tasks for a user"},
#     {"name": "complete_task", "description": "Mark a task as completed"},
#     {"name": "delete_task", "description": "Permanently remove a task"},
#     {"name": "update_task", "description": "Modify task attributes"}
#   ]
# }
```

### 3. View API Documentation

Open browser and navigate to:
- **Swagger UI:** http://localhost:8001/docs
- **ReDoc:** http://localhost:8001/redoc

## Testing MCP Tools

### 1. Test add_task Tool

```bash
curl -X POST http://localhost:8001/tools/add_task \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "title": "Review the proposal",
    "description": "Review and provide feedback on the Q4 proposal",
    "due_date": "2026-02-15T17:00:00Z"
  }'

# Expected response:
# {
#   "status": "success",
#   "task": {
#     "id": 1,
#     "user_id": "user123",
#     "title": "Review the proposal",
#     "description": "Review and provide feedback on the Q4 proposal",
#     "status": "pending",
#     "due_date": "2026-02-15T17:00:00Z",
#     "created_at": "2026-02-09T10:30:00Z",
#     "updated_at": "2026-02-09T10:30:00Z"
#   }
# }

# Save task_id for subsequent tests
export TASK_ID=1
```

### 2. Test list_tasks Tool

```bash
curl -X POST http://localhost:8001/tools/list_tasks \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "status": "pending"
  }'

# Expected response:
# {
#   "status": "success",
#   "tasks": [
#     {
#       "id": 1,
#       "user_id": "user123",
#       "title": "Review the proposal",
#       ...
#     }
#   ]
# }
```

### 3. Test complete_task Tool

```bash
curl -X POST http://localhost:8001/tools/complete_task \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "task_id": '$TASK_ID'
  }'

# Expected response:
# {
#   "status": "success",
#   "task": {
#     "id": 1,
#     "status": "completed",
#     "updated_at": "2026-02-09T14:30:00Z",
#     ...
#   }
# }
```

### 4. Test update_task Tool

```bash
curl -X POST http://localhost:8001/tools/update_task \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "task_id": '$TASK_ID',
    "title": "Review the Q4 proposal",
    "due_date": "2026-02-20T17:00:00Z"
  }'

# Expected response:
# {
#   "status": "success",
#   "task": {
#     "id": 1,
#     "title": "Review the Q4 proposal",
#     "due_date": "2026-02-20T17:00:00Z",
#     "updated_at": "2026-02-09T15:00:00Z",
#     ...
#   }
# }
```

### 5. Test delete_task Tool

```bash
curl -X POST http://localhost:8001/tools/delete_task \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "task_id": '$TASK_ID'
  }'

# Expected response:
# {
#   "status": "success",
#   "message": "Task deleted successfully",
#   "task_id": 1
# }
```

### 6. Test Error Handling

```bash
# Test task not found
curl -X POST http://localhost:8001/tools/complete_task \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "task_id": 999
  }'

# Expected response:
# {
#   "status": "error",
#   "error": {
#     "code": "TASK_NOT_FOUND",
#     "message": "Task with id 999 not found for user user123",
#     "details": {
#       "task_id": 999,
#       "user_id": "user123"
#     }
#   }
# }

# Test validation error
curl -X POST http://localhost:8001/tools/add_task \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "title": ""
  }'

# Expected response:
# {
#   "status": "error",
#   "error": {
#     "code": "VALIDATION_ERROR",
#     "message": "Title must be between 1 and 200 characters",
#     ...
#   }
# }
```

### 7. Test User Isolation

```bash
# Create task for user123
curl -X POST http://localhost:8001/tools/add_task \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user123", "title": "User 123 task"}'

# Try to access with user456 (should fail)
curl -X POST http://localhost:8001/tools/complete_task \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user456", "task_id": 1}'

# Expected response:
# {
#   "status": "error",
#   "error": {
#     "code": "TASK_NOT_FOUND",
#     "message": "Task with id 1 not found for user user456",
#     ...
#   }
# }
```

## Testing with Postman

### 1. Import Collection

Create new Postman collection with these requests:

**Request 1: Add Task**
- Method: POST
- URL: `http://localhost:8001/tools/add_task`
- Headers: `Content-Type: application/json`
- Body (JSON):
  ```json
  {
    "user_id": "{{user_id}}",
    "title": "Test task",
    "description": "Test description"
  }
  ```

**Request 2: List Tasks**
- Method: POST
- URL: `http://localhost:8001/tools/list_tasks`
- Headers: `Content-Type: application/json`
- Body (JSON):
  ```json
  {
    "user_id": "{{user_id}}",
    "status": "all"
  }
  ```

### 2. Set Environment Variables

Create Postman environment with:
- `user_id`: Your test user ID (e.g., "user123")
- `task_id`: Task ID from add_task response

## Troubleshooting

### Database Connection Issues

**Error:** `could not connect to server`

**Solution:**
1. Verify DATABASE_URL is correct
2. Check Neon project is active
3. Verify SSL mode is set: `?sslmode=require`
4. Test connection with psql: `psql $DATABASE_URL`

### MCP SDK Issues

**Error:** `ModuleNotFoundError: No module named 'mcp'`

**Solution:**
1. Verify MCP SDK is installed: `pip list | grep mcp`
2. Install if missing: `pip install mcp-sdk`
3. Check Python version: `python --version` (must be 3.11+)

### Tool Invocation Issues

**Error:** Tool returns `INTERNAL_ERROR`

**Solution:**
1. Check server logs for detailed error
2. Verify database connection is active
3. Check tool parameters match schema
4. Review database migration completed successfully

### Performance Issues

**Symptom:** Tool invocations take > 1 second

**Solution:**
1. Check database query performance with EXPLAIN
2. Verify indexes are created: `\di` in psql
3. Check connection pool settings
4. Monitor database load in Neon dashboard

## Development Workflow

### 1. Make Code Changes

```bash
# Edit files in backend/mcp/
# Server auto-reloads with --reload flag
```

### 2. Run Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_tools.py

# Run with coverage
pytest --cov=backend.mcp --cov-report=html
```

### 3. Format Code

```bash
# Format with black
black backend/mcp/

# Lint with flake8
flake8 backend/mcp/
```

### 4. Check Database State

```bash
# View tasks
psql $DATABASE_URL -c "SELECT id, user_id, title, status, created_at FROM tasks ORDER BY created_at DESC LIMIT 10;"

# Count tasks by user
psql $DATABASE_URL -c "SELECT user_id, COUNT(*) FROM tasks GROUP BY user_id;"

# Count tasks by status
psql $DATABASE_URL -c "SELECT status, COUNT(*) FROM tasks GROUP BY status;"
```

## Integration with AI Agent

### 1. Configure Agent to Use MCP Tools

In AI agent configuration (Spec 2):

```python
from mcp import MCPClient

# Initialize MCP client
mcp_client = MCPClient(base_url="http://localhost:8001")

# Register tools with agent
agent.register_tool("add_task", mcp_client.call_tool)
agent.register_tool("list_tasks", mcp_client.call_tool)
agent.register_tool("complete_task", mcp_client.call_tool)
agent.register_tool("delete_task", mcp_client.call_tool)
agent.register_tool("update_task", mcp_client.call_tool)
```

### 2. Test End-to-End Flow

```bash
# Start MCP server (terminal 1)
uvicorn backend.mcp.server:app --port 8001

# Start AI agent server (terminal 2)
uvicorn backend.main:app --port 8000

# Send chat message (terminal 3)
curl -X POST http://localhost:8000/api/user123/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Create a task to review the proposal"}'

# Expected: Agent invokes add_task tool via MCP
```

## Production Deployment

### 1. Environment Configuration

```bash
# Set production environment variables
ENVIRONMENT=production
LOG_LEVEL=WARNING
DATABASE_URL=<production-database-url>
MCP_SERVER_PORT=8001
```

### 2. Run with Multiple Workers

```bash
# Run with 4 workers for concurrency
uvicorn backend.mcp.server:app --host 0.0.0.0 --port 8001 --workers 4
```

### 3. Use Process Manager

```bash
# Install gunicorn
pip install gunicorn

# Run with gunicorn
gunicorn backend.mcp.server:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8001
```

### 4. Enable HTTPS

Use reverse proxy (nginx, Caddy) or cloud load balancer for TLS termination.

## Next Steps

1. **Integrate with AI Agent:** Connect MCP tools with AI agent (Spec 2)
2. **Add Monitoring:** Implement metrics collection and alerting
3. **Optimize Performance:** Add caching, query optimization
4. **Add Features:** Implement additional tools as needed
5. **Deploy to Production:** Use cloud platform (AWS, GCP, Azure)

## Resources

- **FastAPI Docs:** https://fastapi.tiangolo.com
- **SQLModel Docs:** https://sqlmodel.tiangolo.com
- **MCP SDK Docs:** https://mcp-sdk.readthedocs.io
- **Neon Docs:** https://neon.tech/docs

## Support

For issues or questions:
1. Check troubleshooting section above
2. Review API documentation at `/docs`
3. Check database logs and application logs
4. Review tool schemas in `contracts/tool-schemas.md`
