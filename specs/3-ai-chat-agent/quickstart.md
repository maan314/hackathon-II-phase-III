# Quick Start Guide: AI Chat Agent and Conversation System

**Date:** 2026-02-09
**Feature:** 3-ai-chat-agent
**Audience:** Developers implementing the chat agent

## Overview

This guide provides step-by-step instructions for setting up, implementing, and testing the AI Chat Agent and Conversation System.

---

## Prerequisites

### Required Software
- Python 3.10 or higher
- PostgreSQL (Neon serverless instance)
- Git
- pip (Python package manager)

### Required Accounts
- OpenAI API account with API key
- Neon PostgreSQL database (already configured)
- Access to existing backend repository

### Required Knowledge
- Python and FastAPI basics
- SQLModel ORM
- REST API concepts
- Basic understanding of AI agents

---

## Environment Setup

### Step 1: Install Dependencies

Add the following packages to `requirements.txt`:

```txt
# Existing dependencies
fastapi>=0.104.0
sqlmodel>=0.0.14
uvicorn>=0.24.0
python-jose[cryptography]>=3.3.0
python-multipart>=0.0.6
pydantic>=2.0.0

# New dependencies for AI Chat Agent
openai>=1.10.0
asyncio>=3.4.3
python-dotenv>=1.0.0
```

Install dependencies:

```bash
pip install -r requirements.txt
```

### Step 2: Configure Environment Variables

Add to `.env` file:

```env
# Existing variables
DATABASE_URL=postgresql://user:password@host/database
JWT_SECRET=your-jwt-secret

# New variables for AI Chat Agent
OPENAI_API_KEY=sk-your-openai-api-key-here
AGENT_MODEL=gpt-4-turbo-preview
AGENT_TEMPERATURE=0.7
AGENT_MAX_TOKENS=1000
AGENT_TIMEOUT=30
CONTEXT_WINDOW_SIZE=50
```

**Security Note:** Never commit `.env` file to version control. Add to `.gitignore`.

### Step 3: Verify Database Connection

Test database connectivity:

```bash
python -c "from sqlmodel import create_engine; engine = create_engine('your-database-url'); print('Database connected!')"
```

---

## Database Setup

### Step 1: Create Database Models

Create `backend/models/conversation.py`:

```python
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional, List
from enum import Enum

class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: str = Field(index=True, max_length=255)
    title: Optional[str] = Field(default=None, max_length=500)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[dict] = Field(default=None, sa_column_kwargs={"type_": "JSONB"})

    messages: List["Message"] = Relationship(back_populates="conversation")

class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"

class Message(SQLModel, table=True):
    __tablename__ = "messages"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    conversation_id: UUID = Field(foreign_key="conversations.id", index=True)
    role: MessageRole = Field(sa_column_kwargs={"type_": "VARCHAR(20)"})
    content: str = Field(min_length=1)
    timestamp: datetime = Field(default_factory=datetime.utcnow, index=True)
    tool_calls: Optional[List[dict]] = Field(default=None, sa_column_kwargs={"type_": "JSONB"})
    metadata: Optional[dict] = Field(default=None, sa_column_kwargs={"type_": "JSONB"})

    conversation: Optional[Conversation] = Relationship(back_populates="messages")
```

### Step 2: Create Database Migration

Create migration file `backend/migrations/add_conversation_tables.py`:

```python
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

def upgrade():
    # Create conversations table
    op.create_table(
        'conversations',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', sa.String(255), nullable=False, index=True),
        sa.Column('title', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('metadata', JSONB, nullable=True)
    )

    op.create_index('idx_conversations_user_id', 'conversations', ['user_id'])
    op.create_index('idx_conversations_updated_at', 'conversations', ['updated_at'])

    # Create messages table
    op.create_table(
        'messages',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('conversation_id', UUID(as_uuid=True), nullable=False),
        sa.Column('role', sa.String(20), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False, index=True),
        sa.Column('tool_calls', JSONB, nullable=True),
        sa.Column('metadata', JSONB, nullable=True),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ondelete='CASCADE')
    )

    op.create_index('idx_messages_conversation_id', 'messages', ['conversation_id'])
    op.create_index('idx_messages_timestamp', 'messages', ['timestamp'])

    # Add check constraint for role
    op.create_check_constraint(
        'check_message_role',
        'messages',
        "role IN ('user', 'assistant')"
    )

def downgrade():
    op.drop_table('messages')
    op.drop_table('conversations')
```

### Step 3: Run Migration

```bash
alembic upgrade head
```

Verify tables created:

```bash
psql $DATABASE_URL -c "\dt"
```

Expected output:
```
 conversations
 messages
 tasks (existing)
```

---

## Agent Service Implementation

### Step 1: Create Agent Service

Create `backend/services/agent_service.py`:

```python
import os
import asyncio
from openai import AsyncOpenAI
from typing import List, Dict, Optional

class AgentService:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = os.getenv("AGENT_MODEL", "gpt-4-turbo-preview")
        self.temperature = float(os.getenv("AGENT_TEMPERATURE", "0.7"))
        self.max_tokens = int(os.getenv("AGENT_MAX_TOKENS", "1000"))
        self.timeout = int(os.getenv("AGENT_TIMEOUT", "30"))
        self.system_prompt = self._load_system_prompt()
        self.tools = self._load_tools()

    def _load_system_prompt(self) -> str:
        return """You are a task management assistant. You help users manage their tasks through natural language.

AVAILABLE TOOLS:
1. add_task(title, description, due_date, priority, user_id) - Creates a new task
2. list_tasks(status, due_date_filter, user_id) - Lists tasks with optional filters
3. update_task(task_id, title, description, due_date, priority, user_id) - Updates an existing task
4. complete_task(task_id, user_id) - Marks a task as completed
5. delete_task(task_id, user_id) - Deletes a task permanently

BEHAVIORAL GUIDELINES:
- Always confirm actions before executing tools
- Ask clarifying questions when user intent is ambiguous
- Provide friendly, conversational responses
- Reference previous conversation context when relevant
- Handle errors gracefully with helpful suggestions
"""

    def _load_tools(self) -> List[Dict]:
        # Load MCP tool schemas and convert to OpenAI function format
        return [
            {
                "type": "function",
                "function": {
                    "name": "add_task",
                    "description": "Create a new task",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string"},
                            "description": {"type": "string"},
                            "due_date": {"type": "string"},
                            "priority": {"type": "string"}
                        },
                        "required": ["title"]
                    }
                }
            },
            # Add other tools...
        ]

    async def process_message(
        self,
        user_message: str,
        conversation_history: List[Dict],
        user_id: str
    ) -> Dict:
        try:
            messages = [{"role": "system", "content": self.system_prompt}]
            messages.extend(conversation_history)
            messages.append({"role": "user", "content": user_message})

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

            return {
                "content": response.choices[0].message.content,
                "tool_calls": response.choices[0].message.tool_calls
            }

        except asyncio.TimeoutError:
            raise Exception("Agent processing timeout")
        except Exception as e:
            raise Exception(f"Agent error: {str(e)}")
```

### Step 2: Create Repository Layer

Create `backend/repositories/conversation_repository.py`:

```python
from sqlmodel import Session, select
from typing import List, Optional
from uuid import UUID
from backend.models.conversation import Conversation, Message

class ConversationRepository:
    def __init__(self, session: Session):
        self.session = session

    def create_conversation(self, user_id: str) -> Conversation:
        conversation = Conversation(user_id=user_id)
        self.session.add(conversation)
        self.session.commit()
        self.session.refresh(conversation)
        return conversation

    def get_conversation(self, conversation_id: UUID, user_id: str) -> Optional[Conversation]:
        statement = select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id
        )
        return self.session.exec(statement).first()

    def add_message(
        self,
        conversation_id: UUID,
        role: str,
        content: str,
        tool_calls: Optional[List[dict]] = None
    ) -> Message:
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            tool_calls=tool_calls
        )
        self.session.add(message)
        self.session.commit()
        self.session.refresh(message)
        return message

    def get_messages(self, conversation_id: UUID, limit: int = 50) -> List[Message]:
        statement = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.timestamp.desc())
            .limit(limit)
        )
        messages = self.session.exec(statement).all()
        return list(reversed(messages))  # Chronological order
```

---

## API Endpoint Implementation

### Step 1: Create Chat Endpoint

Create `backend/routers/chat.py`:

```python
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from uuid import UUID

router = APIRouter(prefix="/api/{user_id}/chat", tags=["chat"])

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[UUID] = None

class ChatResponse(BaseModel):
    response: str
    conversation_id: UUID
    message_id: UUID
    timestamp: str
    tool_calls: Optional[list] = None

@router.post("", response_model=ChatResponse)
async def send_message(
    user_id: str,
    request: ChatRequest,
    current_user: str = Depends(get_current_user),
    session: Session = Depends(get_session),
    agent: AgentService = Depends(get_agent_service)
):
    # Verify user_id matches authenticated user
    if user_id != current_user:
        raise HTTPException(status_code=403, detail="Forbidden")

    # Get or create conversation
    repo = ConversationRepository(session)
    if request.conversation_id:
        conversation = repo.get_conversation(request.conversation_id, user_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
    else:
        conversation = repo.create_conversation(user_id)

    # Save user message
    user_message = repo.add_message(
        conversation.id,
        "user",
        request.message
    )

    # Get conversation history
    history = repo.get_messages(conversation.id, limit=50)
    history_formatted = [
        {"role": msg.role, "content": msg.content}
        for msg in history[:-1]  # Exclude current message
    ]

    # Process with agent
    agent_response = await agent.process_message(
        request.message,
        history_formatted,
        user_id
    )

    # Save agent message
    assistant_message = repo.add_message(
        conversation.id,
        "assistant",
        agent_response["content"],
        tool_calls=agent_response.get("tool_calls")
    )

    return ChatResponse(
        response=agent_response["content"],
        conversation_id=conversation.id,
        message_id=assistant_message.id,
        timestamp=assistant_message.timestamp.isoformat(),
        tool_calls=[{"tool_name": tc.function.name, "status": "success"}
                    for tc in agent_response.get("tool_calls", [])]
    )
```

### Step 2: Register Router

In `backend/main.py`:

```python
from backend.routers import chat

app.include_router(chat.router)
```

---

## Testing

### Step 1: Start the Server

```bash
uvicorn backend.main:app --reload --port 8000
```

### Step 2: Test with cURL

**Create new conversation:**

```bash
curl -X POST http://localhost:8000/api/user_123/chat \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Add a task to buy groceries tomorrow"
  }'
```

**Continue conversation:**

```bash
curl -X POST http://localhost:8000/api/user_123/chat \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What tasks do I have?",
    "conversation_id": "550e8400-e29b-41d4-a716-446655440000"
  }'
```

### Step 3: Verify Database

Check conversations:

```bash
psql $DATABASE_URL -c "SELECT * FROM conversations WHERE user_id='user_123';"
```

Check messages:

```bash
psql $DATABASE_URL -c "SELECT * FROM messages WHERE conversation_id='YOUR_CONVERSATION_ID' ORDER BY timestamp;"
```

---

## Troubleshooting

### Issue: OpenAI API Key Invalid

**Error:** `openai.AuthenticationError: Invalid API key`

**Solution:**
1. Verify API key in `.env` file
2. Check key has no extra spaces or quotes
3. Verify key is active in OpenAI dashboard

### Issue: Database Connection Failed

**Error:** `sqlalchemy.exc.OperationalError: could not connect to server`

**Solution:**
1. Verify DATABASE_URL is correct
2. Check Neon database is running
3. Verify network connectivity

### Issue: Agent Timeout

**Error:** `Agent processing timeout`

**Solution:**
1. Increase AGENT_TIMEOUT in `.env`
2. Check OpenAI API status
3. Simplify user message

### Issue: Tool Invocation Failed

**Error:** `Tool execution error`

**Solution:**
1. Verify MCP server is running
2. Check tool schemas match
3. Verify user_id is passed correctly

---

## Next Steps

1. ✅ Environment setup complete
2. ✅ Database models created
3. ✅ Agent service implemented
4. ✅ API endpoint created
5. ⏭️ Implement tool invocation handler
6. ⏭️ Add comprehensive error handling
7. ⏭️ Write integration tests
8. ⏭️ Deploy to production

---

## Additional Resources

- [OpenAI API Documentation](https://platform.openai.com/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
- [Neon PostgreSQL Documentation](https://neon.tech/docs)

---

**Quick Start Version:** 1.0
**Last Updated:** 2026-02-09
**Status:** Ready for implementation
