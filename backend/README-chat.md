# AI Chat Agent Backend

Stateless AI-powered chat backend for task management using Cohere API.

## Architecture

**Stateless Design:**
- No in-memory session storage
- All conversation state persisted in Neon PostgreSQL
- Conversation history reconstructed per request
- Fresh agent instance per request

**User Isolation:**
- user_id enforced in all database queries
- Users can only access their own conversations
- Better Auth integration for production

## Quick Start

### 1. Prerequisites

- Python 3.11+
- Neon PostgreSQL database
- Cohere API key

### 2. Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements-chat.txt

# Copy environment template
cp .env.example .env

# Edit .env with your credentials
# - DATABASE_URL: Your Neon PostgreSQL connection string
# - COHERE_API_KEY: Your Cohere API key
```

### 3. Database Migration

```bash
# Run migrations
python -m backend.db.migrate

# Verify tables created
psql $DATABASE_URL -c "\dt"
```

### 4. Run Server

```bash
# Development mode (auto-reload)
uvicorn backend.main:app --reload --port 8000

# Production mode
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 5. Test Endpoint

```bash
# Send chat message
curl -X POST http://localhost:8000/api/user123/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Create a task to review the proposal"}'

# Expected response:
# {
#   "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
#   "message": "I've created a task titled 'Review the proposal' for you.",
#   "tool_calls": [...],
#   "created_at": "2026-02-09T10:30:00Z"
# }
```

## Project Structure

```
backend/
├── main.py                      # FastAPI application entry point
├── config.py                    # Configuration and environment variables
├── requirements-chat.txt        # Python dependencies
├── .env.example                 # Environment variable template
├── db/
│   ├── models.py                # SQLModel Conversation and Message models
│   ├── connection.py            # Database connection pooling
│   ├── migrate.py               # Migration runner
│   ├── migrations/
│   │   └── 001_initial_schema.sql
│   └── crud/
│       ├── conversations.py     # Conversation CRUD operations
│       └── messages.py          # Message CRUD operations
├── agent/
│   ├── prompts.py               # System prompt definitions
│   ├── agent.py                 # Cohere Agent configuration
│   └── logging.py               # Tool call logging
└── api/
    └── chat.py                  # Chat endpoint implementation
```

## API Endpoints

### POST /api/{user_id}/chat

Send a message to the AI agent.

**Request:**
```json
{
  "message": "Create a task to review the proposal",
  "conversation_id": null  // Optional, null for new conversation
}
```

**Response:**
```json
{
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "I've created a task titled 'Review the proposal' for you.",
  "tool_calls": [
    {
      "tool_name": "create_task",
      "parameters": {"title": "Review the proposal"},
      "result": {"task_id": 123},
      "status": "success",
      "error": null,
      "timestamp": "2026-02-09T10:30:00Z"
    }
  ],
  "created_at": "2026-02-09T10:30:01Z"
}
```

### GET /api/{user_id}/conversations

List user's conversations.

### GET /api/{user_id}/conversations/{conversation_id}/messages

Get all messages for a conversation.

### GET /health

Health check endpoint.

## Key Features

✅ **Stateless Architecture**: No in-memory session storage
✅ **Conversation Persistence**: All messages stored in Neon PostgreSQL
✅ **User Isolation**: user_id enforced in all queries
✅ **Tool Call Logging**: Complete audit trail of agent actions
✅ **Error Handling**: Graceful handling of failures

## Development

### Run Tests

```bash
pytest
```

### Format Code

```bash
black backend/
flake8 backend/
```

### Database Operations

```bash
# Connect to database
psql $DATABASE_URL

# View conversations
SELECT id, user_id, created_at FROM conversations ORDER BY created_at DESC LIMIT 10;

# View messages
SELECT conversation_id, role, content, created_at FROM messages ORDER BY created_at DESC LIMIT 10;
```

## Troubleshooting

See `specs/2-ai-chat-agent/quickstart.md` for detailed troubleshooting guide.

## Documentation

- **Specification:** `specs/2-ai-chat-agent/spec.md`
- **Implementation Plan:** `specs/2-ai-chat-agent/plan.md`
- **Tasks:** `specs/2-ai-chat-agent/tasks.md`
- **Data Model:** `specs/2-ai-chat-agent/data-model.md`
- **API Contracts:** `specs/2-ai-chat-agent/contracts/`
