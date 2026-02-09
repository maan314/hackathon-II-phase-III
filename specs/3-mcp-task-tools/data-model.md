# Data Model: MCP Server and Task Tooling System

**Feature:** 3-mcp-task-tools
**Date:** 2026-02-09
**Purpose:** Define database entities, relationships, and validation rules

## Entity Definitions

### Task

Represents a todo item for a user.

**Table Name:** `tasks`

**Columns:**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Unique task identifier |
| user_id | VARCHAR(255) | NOT NULL, INDEXED | Owner of the task |
| title | VARCHAR(200) | NOT NULL | Task title |
| description | TEXT | NULLABLE | Task description (max 2000 chars) |
| status | VARCHAR(20) | NOT NULL, DEFAULT 'pending' | Task status (pending/completed) |
| due_date | TIMESTAMP | NULLABLE | Optional due date |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | When task was created |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last modification timestamp |

**Indexes:**
- Primary: `id` (automatic)
- Secondary: `user_id` for user task queries
- Secondary: `created_at` for chronological ordering
- Composite: `(user_id, status)` for filtered queries
- Composite: `(user_id, created_at DESC)` for user task listing

**Constraints:**
- `status` CHECK (status IN ('pending', 'completed'))
- `title` CHECK (length(title) >= 1 AND length(title) <= 200)
- `description` CHECK (description IS NULL OR length(description) <= 2000)

**Relationships:**
- None (single entity model for hackathon scope)

**Validation Rules:**
- `user_id`: Non-empty string, max 255 characters
- `title`: Non-empty string, 1-200 characters
- `description`: String, max 2000 characters if provided
- `status`: Must be 'pending' or 'completed'
- `due_date`: ISO 8601 format if provided
- `created_at`: Auto-generated, immutable
- `updated_at`: Auto-updated on modifications

**SQLModel Definition:**
```python
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional
from enum import Enum

class TaskStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"

class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True, max_length=255)
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)
    status: TaskStatus = Field(default=TaskStatus.PENDING, sa_column_kwargs={"type_": "VARCHAR(20)"})
    due_date: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "user_id": "user123",
                "title": "Review the proposal",
                "description": "Review and provide feedback on the Q4 proposal",
                "status": "pending",
                "due_date": "2026-02-15T17:00:00Z",
                "created_at": "2026-02-09T10:30:00Z",
                "updated_at": "2026-02-09T10:30:00Z"
            }
        }
```

---

## Database Migration Script

**File:** `backend/mcp/db/migrations/001_create_tasks_table.sql`

```sql
-- Create tasks table
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    title VARCHAR(200) NOT NULL CHECK (length(title) >= 1),
    description TEXT CHECK (description IS NULL OR length(description) <= 2000),
    status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'completed')),
    due_date TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Create index for user task queries
CREATE INDEX idx_tasks_user_id ON tasks(user_id);

-- Create index for chronological ordering
CREATE INDEX idx_tasks_created_at ON tasks(created_at DESC);

-- Create composite index for filtered queries
CREATE INDEX idx_tasks_user_status ON tasks(user_id, status);

-- Create composite index for user task listing
CREATE INDEX idx_tasks_user_created ON tasks(user_id, created_at DESC);

-- Create trigger to auto-update updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_tasks_updated_at BEFORE UPDATE ON tasks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

---

## Query Patterns

### Create Task
```python
def create_task(user_id: str, title: str, description: Optional[str] = None,
                due_date: Optional[datetime] = None) -> Task:
    with Session(engine) as session:
        task = Task(
            user_id=user_id,
            title=title,
            description=description,
            due_date=due_date,
            status=TaskStatus.PENDING
        )
        session.add(task)
        session.commit()
        session.refresh(task)
        return task
```

### List Tasks
```python
def list_tasks(user_id: str, status: Optional[TaskStatus] = None,
               limit: int = 100) -> List[Task]:
    with Session(engine) as session:
        query = session.query(Task).filter(Task.user_id == user_id)

        if status and status != "all":
            query = query.filter(Task.status == status)

        tasks = query.order_by(Task.created_at.desc()).limit(limit).all()
        return tasks
```

### Get Task (with User Isolation)
```python
def get_task(user_id: str, task_id: int) -> Optional[Task]:
    with Session(engine) as session:
        task = session.query(Task).filter(
            Task.id == task_id,
            Task.user_id == user_id
        ).first()
        return task
```

### Update Task
```python
def update_task(user_id: str, task_id: int, **updates) -> Task:
    with Session(engine) as session:
        task = session.query(Task).filter(
            Task.id == task_id,
            Task.user_id == user_id
        ).first()

        if not task:
            raise TaskNotFoundError(task_id, user_id)

        for key, value in updates.items():
            if value is not None and hasattr(task, key):
                setattr(task, key, value)

        task.updated_at = datetime.utcnow()
        session.commit()
        session.refresh(task)
        return task
```

### Complete Task
```python
def complete_task(user_id: str, task_id: int) -> Task:
    with Session(engine) as session:
        task = session.query(Task).filter(
            Task.id == task_id,
            Task.user_id == user_id
        ).first()

        if not task:
            raise TaskNotFoundError(task_id, user_id)

        task.status = TaskStatus.COMPLETED
        task.updated_at = datetime.utcnow()
        session.commit()
        session.refresh(task)
        return task
```

### Delete Task
```python
def delete_task(user_id: str, task_id: int) -> bool:
    with Session(engine) as session:
        task = session.query(Task).filter(
            Task.id == task_id,
            Task.user_id == user_id
        ).first()

        if not task:
            raise TaskNotFoundError(task_id, user_id)

        session.delete(task)
        session.commit()
        return True
```

---

## Performance Considerations

### Index Strategy
- **Primary Key (id)**: Automatic B-tree index for fast lookups
- **user_id**: Index for filtering tasks by user
- **created_at**: Index for chronological ordering
- **(user_id, status)**: Composite index for filtered queries (e.g., list pending tasks)
- **(user_id, created_at DESC)**: Composite index for user task listing with ordering

### Query Optimization
- Use `LIMIT` on list queries to prevent large result sets
- Leverage composite indexes for common query patterns
- Use connection pooling to reduce connection overhead
- Consider pagination for users with > 100 tasks (future enhancement)

### Data Size Estimates
- Task: ~300-500 bytes per row (depending on description length)
- 1000 users with 50 tasks each: ~15-25 MB
- Indexes add ~20-30% overhead
- Neon auto-scales storage as needed

---

## Security Considerations

### User Isolation
- All queries MUST filter by user_id
- Task ownership verified before any operation
- No cross-user data access possible

### Input Validation
- Title limited to 200 characters
- Description limited to 2000 characters
- Status restricted to enum values
- Due date validated as ISO 8601 format

### Data Protection
- Use parameterized queries to prevent SQL injection
- Database connections use TLS encryption (Neon default)
- No sensitive data stored in tasks (design assumption)

---

## Future Enhancements

### Task Metadata
- Add tags for categorization
- Add priority field (low, medium, high)
- Add assignee field for task delegation

### Task Relationships
- Add parent_task_id for subtasks
- Add task dependencies (blocked_by)

### Performance Optimizations
- Implement soft delete (deleted_at field)
- Add task archival for completed tasks
- Implement full-text search on title/description

### Analytics
- Track task completion rates
- Track average time to completion
- Add task activity history table
