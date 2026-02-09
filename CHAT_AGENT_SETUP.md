# AI Chat Agent - Phase III Setup

## Quick Start (Separate Server)

The AI Chat Agent runs as a **separate server** on port 8002, so it won't interfere with your existing backend.

### 1. Start the Chat Agent Server

```bash
cd backend
python chat_server.py
```

Or with uvicorn:
```bash
uvicorn backend.chat_server:app --reload --port 8002
```

### 2. Test the Chat Endpoint

```bash
# Test health check
curl http://localhost:8002/health

# Send a chat message
curl -X POST http://localhost:8002/api/user_123/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What tasks do I have?"}'
```

## Server Ports

- **Your existing backend**: Port 8000 (unchanged)
- **Chat Agent server**: Port 8002 (new, separate)

## What Was Added (No Changes to Existing Code)

### New Files Created:
1. `backend/chat_server.py` - Standalone chat server
2. `backend/models/conversation.py` - Conversation & Message models
3. `backend/repositories/conversation_repository.py` - Data access layer
4. `backend/services/agent_service.py` - OpenAI agent integration
5. `backend/services/tool_handler.py` - Tool invocation handler
6. `backend/services/context_manager.py` - Context window management
7. `backend/routers/chat.py` - Chat API endpoint
8. `backend/db/migrations/003_create_conversation_tables.sql` - Database migration
9. `tests/test_chat_integration.py` - Integration tests

### Database Tables Added:
- `conversations` - Stores conversation threads
- `messages` - Stores individual messages

### Dependencies Added to requirements.txt:
- `openai>=1.10.0` - OpenAI SDK
- `alembic>=1.13.0` - Database migrations

## Environment Variables (Already in .env)

```env
# OpenAI Configuration
OPENAI_API_KEY=sk-proj-...
AGENT_MODEL=gpt-4-turbo-preview
AGENT_TEMPERATURE=0.7
AGENT_MAX_TOKENS=1000
AGENT_TIMEOUT=30
CONTEXT_WINDOW_SIZE=50
```

## API Endpoint

**POST /api/{user_id}/chat**

Request:
```json
{
  "message": "Add a task to buy groceries tomorrow",
  "conversation_id": "optional-uuid"
}
```

Response:
```json
{
  "response": "I've added 'Buy groceries' to your tasks",
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "message_id": "660e8400-e29b-41d4-a716-446655440001",
  "timestamp": "2026-02-09T21:00:00Z",
  "tool_calls": [{"tool_name": "add_task", "status": "success"}]
}
```

## Integration with Your Existing Backend

If you want to integrate the chat functionality into your existing backend later:

1. Import the chat router in your main.py:
   ```python
   from routers.chat import router as chat_router
   app.include_router(chat_router)
   ```

2. Or keep it as a separate microservice on port 8002

## Running Both Servers

```bash
# Terminal 1: Your existing backend
cd backend
uvicorn main:app --reload --port 8000

# Terminal 2: Chat agent server
cd backend
python chat_server.py
```

## Testing

```bash
# Run integration tests
pytest tests/test_chat_integration.py -v
```

## Troubleshooting

**Port 8002 already in use:**
```bash
# Change port in chat_server.py or use:
uvicorn backend.chat_server:app --reload --port 8003
```

**OpenAI API errors:**
- Verify OPENAI_API_KEY in .env
- Check API key has credits

**Database connection:**
- Uses same DATABASE_URL as your existing backend
- Migration creates new tables without affecting existing ones
