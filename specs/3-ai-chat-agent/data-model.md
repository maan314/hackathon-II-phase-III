# Data Model: AI Chat Agent and Conversation System

**Date:** 2026-02-09
**Feature:** 3-ai-chat-agent
**Phase:** Phase 1 - Design

## Overview

This document defines the data entities, relationships, validation rules, and state transitions for the AI Chat Agent and Conversation System.

---

## Entity Definitions

### Entity 1: Conversation

**Purpose:** Represents a conversation thread between a user and the AI agent.

**Fields:**

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PRIMARY KEY, NOT NULL | Unique identifier for the conversation |
| user_id | VARCHAR(255) | NOT NULL, INDEXED | User who owns this conversation |
| title | VARCHAR(500) | NULLABLE | Optional conversation title (auto-generated or user-provided) |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | When the conversation was created |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | When the conversation was last updated |
| metadata | JSONB | NULLABLE | Additional conversation metadata (tags, status, etc.) |

**Indexes:**
- `idx_conversations_user_id` on `user_id` (for user conversation list queries)
- `idx_conversations_updated_at` on `updated_at DESC` (for recent conversations)

**Validation Rules:**
- `id` must be valid UUID v4
- `user_id` must be non-empty string
- `title` max length 500 characters
- `created_at` must be <= `updated_at`
- `metadata` must be valid JSON if provided

**SQLModel Definition:**
```python
from sqlmodel import SQLModel, Field
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional

class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: str = Field(index=True, max_length=255)
    title: Optional[str] = Field(default=None, max_length=500)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[dict] = Field(default=None, sa_column_kwargs={"type_": "JSONB"})
```

---

### Entity 2: Message

**Purpose:** Represents a single message within a conversation (user or assistant).

**Fields:**

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PRIMARY KEY, NOT NULL | Unique identifier for the message |
| conversation_id | UUID | FOREIGN KEY, NOT NULL, INDEXED | Reference to parent conversation |
| role | VARCHAR(20) | NOT NULL, CHECK IN ('user', 'assistant') | Message sender role |
| content | TEXT | NOT NULL | Message text content |
| timestamp | TIMESTAMP | NOT NULL, DEFAULT NOW(), INDEXED | When the message was created |
| tool_calls | JSONB | NULLABLE | Tool invocations made by agent (if role=assistant) |
| metadata | JSONB | NULLABLE | Additional message metadata |

**Indexes:**
- `idx_messages_conversation_id` on `conversation_id` (for message retrieval)
- `idx_messages_timestamp` on `timestamp DESC` (for chronological ordering)

**Validation Rules:**
- `id` must be valid UUID v4
- `conversation_id` must reference existing conversation
- `role` must be exactly "user" or "assistant"
- `content` must be non-empty string
- `timestamp` must be chronologically consistent within conversation
- `tool_calls` must be valid JSON array if provided

**SQLModel Definition:**
```python
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional, List
from enum import Enum

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

    # Relationship
    conversation: Optional[Conversation] = Relationship(back_populates="messages")
```

---

### Entity 3: Tool Invocation (Embedded in Message)

**Purpose:** Records details of tool invocations made by the agent.

**Structure (JSON within Message.tool_calls):**
```json
{
  "tool_calls": [
    {
      "tool_name": "add_task",
      "arguments": {
        "title": "Buy groceries",
        "due_date": "2026-02-10",
        "user_id": "user_123"
      },
      "result": {
        "status": "success",
        "data": {
          "task_id": "task_456",
          "title": "Buy groceries",
          "created_at": "2026-02-09T20:00:00Z"
        }
      },
      "execution_time_ms": 145,
      "timestamp": "2026-02-09T20:00:00Z"
    }
  ]
}
```

**Fields:**
- `tool_name`: Name of the invoked tool
- `arguments`: Parameters passed to the tool
- `result.status`: "success" or "error"
- `result.data`: Tool response data (if successful)
- `result.error`: Error details (if failed)
- `execution_time_ms`: Tool execution duration
- `timestamp`: When the tool was invoked

---

## Relationships

### Conversation ↔ Message (One-to-Many)

**Relationship:** One Conversation has many Messages

**Foreign Key:** `Message.conversation_id` → `Conversation.id`

**Cascade Behavior:** ON DELETE CASCADE (deleting conversation deletes all messages)

**SQLModel Relationship:**
```python
class Conversation(SQLModel, table=True):
    # ... fields ...
    messages: List["Message"] = Relationship(back_populates="conversation")

class Message(SQLModel, table=True):
    # ... fields ...
    conversation: Optional[Conversation] = Relationship(back_populates="messages")
```

### User ↔ Conversation (Implicit, via user_id)

**Relationship:** One User has many Conversations

**Implementation:** User isolation enforced at query level (filter by user_id)

**No Foreign Key:** user_id is a string identifier from JWT, not a database FK

---

## Validation Rules

### Conversation Validation

1. **User Isolation:**
   - All queries MUST filter by user_id
   - Users cannot access conversations where user_id doesn't match

2. **Title Generation:**
   - If title is null, auto-generate from first user message (first 50 chars)
   - Title updated on conversation creation or explicit user request

3. **Timestamp Consistency:**
   - `updated_at` must be >= `created_at`
   - `updated_at` updated whenever new message added

### Message Validation

1. **Role Validation:**
   - Role must be "user" or "assistant"
   - Messages must alternate between user and assistant (soft rule, not enforced)

2. **Content Validation:**
   - Content must be non-empty
   - Content max length: 10,000 characters (prevent abuse)

3. **Chronological Ordering:**
   - Messages within a conversation must be chronologically ordered
   - Timestamp must be >= conversation.created_at

4. **Tool Calls Validation:**
   - tool_calls only valid when role = "assistant"
   - tool_calls must be valid JSON array
   - Each tool call must have: tool_name, arguments, result

---

## State Transitions

### Conversation Lifecycle

```
[New] → [Active] → [Archived]
  ↓         ↓
[Deleted] [Deleted]
```

**States:**
- **New:** Conversation just created, no messages yet
- **Active:** Conversation has messages, user actively engaging
- **Archived:** Conversation inactive for extended period (future feature)
- **Deleted:** Conversation soft-deleted (future feature)

**Current Implementation:** Only New and Active states (no archival or soft delete)

### Message Lifecycle

```
[Created] → [Persisted]
```

**States:**
- **Created:** Message object created in memory
- **Persisted:** Message saved to database

**Immutability:** Messages are immutable once persisted (no updates or deletes)

---

## Query Patterns

### Common Queries

1. **Get User's Conversations:**
```sql
SELECT * FROM conversations
WHERE user_id = ?
ORDER BY updated_at DESC
LIMIT 20;
```

2. **Get Conversation Messages:**
```sql
SELECT * FROM messages
WHERE conversation_id = ?
ORDER BY timestamp ASC
LIMIT 50;
```

3. **Get Recent Messages (Context Window):**
```sql
SELECT * FROM messages
WHERE conversation_id = ?
ORDER BY timestamp DESC
LIMIT 50;
```

4. **Create New Conversation:**
```sql
INSERT INTO conversations (id, user_id, created_at, updated_at)
VALUES (?, ?, NOW(), NOW())
RETURNING *;
```

5. **Add Message:**
```sql
INSERT INTO messages (id, conversation_id, role, content, timestamp)
VALUES (?, ?, ?, ?, NOW())
RETURNING *;
```

### Query Optimization

- All queries use indexed columns (user_id, conversation_id, timestamp)
- LIMIT clauses prevent unbounded result sets
- Timestamps indexed for efficient ordering
- Foreign key indexes enable fast joins

---

## Data Integrity

### Constraints

1. **Referential Integrity:**
   - Message.conversation_id must reference valid Conversation.id
   - Enforced by FOREIGN KEY constraint

2. **User Isolation:**
   - Application-level enforcement (not database constraint)
   - All queries include user_id filter

3. **Role Constraint:**
   - CHECK constraint ensures role IN ('user', 'assistant')

4. **Non-Null Constraints:**
   - Critical fields (id, user_id, conversation_id, role, content) are NOT NULL

### Data Consistency

1. **Timestamp Consistency:**
   - updated_at automatically updated on message insert (via trigger or application logic)

2. **Tool Call Consistency:**
   - tool_calls only present when role = "assistant"
   - Validated at application layer

3. **Conversation Context:**
   - Messages always associated with valid conversation
   - Orphaned messages prevented by foreign key constraint

---

## Migration Strategy

### Initial Migration

```sql
-- Create conversations table
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(255) NOT NULL,
    title VARCHAR(500),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    metadata JSONB
);

CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_conversations_updated_at ON conversations(updated_at DESC);

-- Create messages table
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    tool_calls JSONB,
    metadata JSONB
);

CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_timestamp ON messages(timestamp DESC);
```

### Rollback Strategy

```sql
DROP TABLE IF EXISTS messages CASCADE;
DROP TABLE IF EXISTS conversations CASCADE;
```

---

## Performance Considerations

### Expected Data Volume

- **Conversations:** ~100 per user (typical)
- **Messages:** ~50-200 per conversation (typical)
- **Total Messages:** ~10,000 per user (typical)

### Index Impact

- Indexes improve query performance by 10-100x
- Index maintenance overhead minimal for expected data volume
- JSONB indexes not needed for current use case

### Scaling Strategy

- Horizontal scaling via user_id sharding (future)
- Conversation archival for old conversations (future)
- Message pagination for very long conversations (future)

---

## Summary

**Entities:** 2 primary (Conversation, Message) + 1 embedded (Tool Invocation)

**Relationships:** 1 (Conversation → Messages, one-to-many)

**Indexes:** 4 (user_id, updated_at, conversation_id, timestamp)

**Validation:** User isolation, role constraints, chronological ordering

**State:** Simple lifecycle (New → Active)

**Ready for:** Implementation in Task 1 (Database Models and Migrations)
