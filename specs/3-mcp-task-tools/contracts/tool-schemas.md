# MCP Tool Schemas

**Feature:** 3-mcp-task-tools
**Purpose:** Define JSON schemas for all MCP tool inputs and outputs

## Tool Schema Definitions

### 1. add_task

**Description:** Create a new task for a user

**Input Schema:**
```json
{
  "type": "object",
  "required": ["user_id", "title"],
  "properties": {
    "user_id": {
      "type": "string",
      "minLength": 1,
      "maxLength": 255,
      "description": "User identifier"
    },
    "title": {
      "type": "string",
      "minLength": 1,
      "maxLength": 200,
      "description": "Task title"
    },
    "description": {
      "type": "string",
      "maxLength": 2000,
      "description": "Task description (optional)"
    },
    "due_date": {
      "type": "string",
      "format": "date-time",
      "description": "Due date in ISO 8601 format (optional)"
    }
  }
}
```

**Output Schema (Success):**
```json
{
  "type": "object",
  "required": ["status", "task"],
  "properties": {
    "status": {
      "type": "string",
      "enum": ["success"]
    },
    "task": {
      "type": "object",
      "required": ["id", "user_id", "title", "status", "created_at", "updated_at"],
      "properties": {
        "id": {"type": "integer"},
        "user_id": {"type": "string"},
        "title": {"type": "string"},
        "description": {"type": ["string", "null"]},
        "status": {"type": "string", "enum": ["pending", "completed"]},
        "due_date": {"type": ["string", "null"], "format": "date-time"},
        "created_at": {"type": "string", "format": "date-time"},
        "updated_at": {"type": "string", "format": "date-time"}
      }
    }
  }
}
```

**Example Request:**
```json
{
  "user_id": "user123",
  "title": "Review the proposal",
  "description": "Review and provide feedback on the Q4 proposal",
  "due_date": "2026-02-15T17:00:00Z"
}
```

**Example Response:**
```json
{
  "status": "success",
  "task": {
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

### 2. list_tasks

**Description:** Retrieve all tasks for a user, optionally filtered by status

**Input Schema:**
```json
{
  "type": "object",
  "required": ["user_id"],
  "properties": {
    "user_id": {
      "type": "string",
      "minLength": 1,
      "maxLength": 255,
      "description": "User identifier"
    },
    "status": {
      "type": "string",
      "enum": ["pending", "completed", "all"],
      "default": "all",
      "description": "Filter tasks by status (optional)"
    }
  }
}
```

**Output Schema (Success):**
```json
{
  "type": "object",
  "required": ["status", "tasks"],
  "properties": {
    "status": {"type": "string", "enum": ["success"]},
    "tasks": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["id", "user_id", "title", "status", "created_at", "updated_at"],
        "properties": {
          "id": {"type": "integer"},
          "user_id": {"type": "string"},
          "title": {"type": "string"},
          "description": {"type": ["string", "null"]},
          "status": {"type": "string", "enum": ["pending", "completed"]},
          "due_date": {"type": ["string", "null"], "format": "date-time"},
          "created_at": {"type": "string", "format": "date-time"},
          "updated_at": {"type": "string", "format": "date-time"}
        }
      }
    }
  }
}
```

**Example Request:**
```json
{
  "user_id": "user123",
  "status": "pending"
}
```

**Example Response:**
```json
{
  "status": "success",
  "tasks": [
    {
      "id": 1,
      "user_id": "user123",
      "title": "Review the proposal",
      "description": "Review and provide feedback on the Q4 proposal",
      "status": "pending",
      "due_date": "2026-02-15T17:00:00Z",
      "created_at": "2026-02-09T10:30:00Z",
      "updated_at": "2026-02-09T10:30:00Z"
    },
    {
      "id": 2,
      "user_id": "user123",
      "title": "Write documentation",
      "description": null,
      "status": "pending",
      "due_date": null,
      "created_at": "2026-02-09T11:00:00Z",
      "updated_at": "2026-02-09T11:00:00Z"
    }
  ]
}
```

---

### 3. complete_task

**Description:** Mark a task as completed

**Input Schema:**
```json
{
  "type": "object",
  "required": ["user_id", "task_id"],
  "properties": {
    "user_id": {
      "type": "string",
      "minLength": 1,
      "maxLength": 255,
      "description": "User identifier"
    },
    "task_id": {
      "type": "integer",
      "minimum": 1,
      "description": "Task identifier"
    }
  }
}
```

**Output Schema (Success):**
```json
{
  "type": "object",
  "required": ["status", "task"],
  "properties": {
    "status": {"type": "string", "enum": ["success"]},
    "task": {
      "type": "object",
      "required": ["id", "user_id", "title", "status", "created_at", "updated_at"],
      "properties": {
        "id": {"type": "integer"},
        "user_id": {"type": "string"},
        "title": {"type": "string"},
        "description": {"type": ["string", "null"]},
        "status": {"type": "string", "enum": ["completed"]},
        "due_date": {"type": ["string", "null"], "format": "date-time"},
        "created_at": {"type": "string", "format": "date-time"},
        "updated_at": {"type": "string", "format": "date-time"}
      }
    }
  }
}
```

**Example Request:**
```json
{
  "user_id": "user123",
  "task_id": 1
}
```

**Example Response:**
```json
{
  "status": "success",
  "task": {
    "id": 1,
    "user_id": "user123",
    "title": "Review the proposal",
    "description": "Review and provide feedback on the Q4 proposal",
    "status": "completed",
    "due_date": "2026-02-15T17:00:00Z",
    "created_at": "2026-02-09T10:30:00Z",
    "updated_at": "2026-02-09T14:30:00Z"
  }
}
```

---

### 4. delete_task

**Description:** Permanently remove a task

**Input Schema:**
```json
{
  "type": "object",
  "required": ["user_id", "task_id"],
  "properties": {
    "user_id": {
      "type": "string",
      "minLength": 1,
      "maxLength": 255,
      "description": "User identifier"
    },
    "task_id": {
      "type": "integer",
      "minimum": 1,
      "description": "Task identifier"
    }
  }
}
```

**Output Schema (Success):**
```json
{
  "type": "object",
  "required": ["status", "message"],
  "properties": {
    "status": {"type": "string", "enum": ["success"]},
    "message": {"type": "string"},
    "task_id": {"type": "integer"}
  }
}
```

**Example Request:**
```json
{
  "user_id": "user123",
  "task_id": 1
}
```

**Example Response:**
```json
{
  "status": "success",
  "message": "Task deleted successfully",
  "task_id": 1
}
```

---

### 5. update_task

**Description:** Modify task attributes (partial update)

**Input Schema:**
```json
{
  "type": "object",
  "required": ["user_id", "task_id"],
  "properties": {
    "user_id": {
      "type": "string",
      "minLength": 1,
      "maxLength": 255,
      "description": "User identifier"
    },
    "task_id": {
      "type": "integer",
      "minimum": 1,
      "description": "Task identifier"
    },
    "title": {
      "type": "string",
      "minLength": 1,
      "maxLength": 200,
      "description": "New task title (optional)"
    },
    "description": {
      "type": "string",
      "maxLength": 2000,
      "description": "New task description (optional)"
    },
    "due_date": {
      "type": "string",
      "format": "date-time",
      "description": "New due date in ISO 8601 format (optional)"
    }
  }
}
```

**Output Schema (Success):**
```json
{
  "type": "object",
  "required": ["status", "task"],
  "properties": {
    "status": {"type": "string", "enum": ["success"]},
    "task": {
      "type": "object",
      "required": ["id", "user_id", "title", "status", "created_at", "updated_at"],
      "properties": {
        "id": {"type": "integer"},
        "user_id": {"type": "string"},
        "title": {"type": "string"},
        "description": {"type": ["string", "null"]},
        "status": {"type": "string", "enum": ["pending", "completed"]},
        "due_date": {"type": ["string", "null"], "format": "date-time"},
        "created_at": {"type": "string", "format": "date-time"},
        "updated_at": {"type": "string", "format": "date-time"}
      }
    }
  }
}
```

**Example Request:**
```json
{
  "user_id": "user123",
  "task_id": 1,
  "title": "Review the Q4 proposal",
  "due_date": "2026-02-20T17:00:00Z"
}
```

**Example Response:**
```json
{
  "status": "success",
  "task": {
    "id": 1,
    "user_id": "user123",
    "title": "Review the Q4 proposal",
    "description": "Review and provide feedback on the Q4 proposal",
    "status": "pending",
    "due_date": "2026-02-20T17:00:00Z",
    "created_at": "2026-02-09T10:30:00Z",
    "updated_at": "2026-02-09T15:00:00Z"
  }
}
```

---

## Error Response Schema (All Tools)

**Schema:**
```json
{
  "type": "object",
  "required": ["status", "error"],
  "properties": {
    "status": {
      "type": "string",
      "enum": ["error"]
    },
    "error": {
      "type": "object",
      "required": ["code", "message"],
      "properties": {
        "code": {
          "type": "string",
          "description": "Machine-readable error code"
        },
        "message": {
          "type": "string",
          "description": "Human-readable error message"
        },
        "details": {
          "type": "object",
          "description": "Additional error context (optional)"
        }
      }
    }
  }
}
```

**Error Codes:**
- `VALIDATION_ERROR`: Input validation failed
- `TASK_NOT_FOUND`: Task doesn't exist or user doesn't have access
- `DATABASE_ERROR`: Database operation failed
- `INTERNAL_ERROR`: Unexpected error

**Example Error Response (Task Not Found):**
```json
{
  "status": "error",
  "error": {
    "code": "TASK_NOT_FOUND",
    "message": "Task with id 999 not found for user user123",
    "details": {
      "task_id": 999,
      "user_id": "user123"
    }
  }
}
```

**Example Error Response (Validation Error):**
```json
{
  "status": "error",
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Title must be between 1 and 200 characters",
    "details": {
      "field": "title",
      "constraint": "minLength: 1, maxLength: 200",
      "value_length": 0
    }
  }
}
```

---

## Schema Validation

All tools validate inputs and outputs against these schemas using Pydantic. Validation failures return structured error responses with specific field-level details.

**Validation Process:**
1. Parse request JSON
2. Validate against input schema
3. Execute tool logic
4. Validate response against output schema
5. Return formatted response

**Benefits:**
- Prevents invalid data from entering system
- Provides clear error messages
- Enables automatic API documentation
- Ensures consistent response format
