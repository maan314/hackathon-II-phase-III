# Implementation Plan: MCP Server and Task Tooling System

## Feature Context

**Feature:** MCP Server and Task Tooling System
**Branch:** 3-mcp-task-tools
**Spec:** specs/3-mcp-task-tools/spec.md

## Technical Context

**Architecture:** MCP server exposing 5 stateless CRUD tools via HTTP. Each tool validates parameters against JSON schemas, executes pure database operations via SQLModel, and returns structured responses. Tools enforce user isolation through user_id filtering. No in-memory state maintained between invocations.

**Technologies:**
- MCP Framework: Official MCP SDK (Python)
- Backend Framework: FastAPI (for HTTP transport)
- ORM: SQLModel (Pydantic + SQLAlchemy)
- Database: Neon PostgreSQL (serverless Postgres)
- Schema Validation: Pydantic models (built into SQLModel)
- Tool Registration: MCP SDK tool decorators

**Infrastructure:**
- Database: Neon PostgreSQL with connection pooling
- MCP Server: FastAPI application with MCP SDK integration
- HTTP Transport: Standard HTTP POST for tool invocations
- Environment: Python 3.11+

**Security:**
- User isolation via user_id parameter in all tools
- Input validation on all tool parameters
- Database queries filtered by user_id
- Parameterized queries to prevent SQL injection
- Error messages sanitized (no internal details leaked)

## Constitution Check

**Principles Applied:**
- Principle 1: Stateless Server Architecture with Persistent Conversation Storage
  - ✅ MCP server is stateless
  - ✅ All task data persisted in Neon PostgreSQL
  - ✅ No in-memory session state

- Principle 2: Tool-Driven AI Behavior (MCP tools only)
  - ✅ Tools are exclusive interface for task mutations
  - ✅ No direct database access outside tools
  - ✅ All operations through MCP tool invocations

- Principle 6: Tools as Exclusive Interface for Task Mutation
  - ✅ All task CRUD operations via MCP tools
  - ✅ No alternative mutation paths
  - ✅ Single source of truth for task operations

- Principle 7: Stateless MCP Server with Database Persistence
  - ✅ Tools do not maintain in-memory state
  - ✅ All data persisted in Neon PostgreSQL
  - ✅ State retrieved per tool invocation

- Principle 8: Tool Schema Strict Validation
  - ✅ All tools validate inputs against JSON schemas
  - ✅ All tools validate outputs against schemas
  - ✅ Validation failures return structured errors

- Principle 9: Agent-Tool Separation of Concerns
  - ✅ Tools contain only pure CRUD operations
  - ✅ No AI logic in tools
  - ✅ No natural language processing in tools

**Key Standards Compliance:**
- Chat state persisted in Neon PostgreSQL ✅
- Agent uses MCP tools only for task modifications ✅
- No in-memory session state ✅
- MCP tools match provided JSON schemas exactly ✅
- Tools persist all state changes in Neon PostgreSQL ✅
- MCP tools contain only pure CRUD operations (no AI logic) ✅
- Every tool invocation returns structured response ✅
- Every MCP tool invocation includes user_id as required parameter ✅
- MCP tools enforce user-level data isolation at database query level ✅

**Constraints Verification:**
- Backend: FastAPI + OpenAI Agents SDK ✅
- ORM: SQLModel | Database: Neon PostgreSQL ✅
- MCP SDK: Official MCP SDK for server and tools ✅
- MCP Tools: add_task, list_tasks, complete_task, delete_task, update_task ✅
- JWT User Identity: user_id extracted from JWT and propagated to all tool calls ✅

**Compliance Status:**
- ✅ All constitutional principles satisfied by design
- ✅ No conflicts identified
- ✅ Architecture aligns with stateless, tool-driven, schema-validated requirements

## Gates

### Gate 1: Requirements Clarity
- [x] All functional requirements are understood
- [x] All non-functional requirements are understood
- [x] All constraints are understood
- [x] All success criteria are understood

### Gate 2: Technical Feasibility
- [x] Architecture supports all requirements (stateless MCP tools with DB persistence)
- [x] Technology choices enable required functionality (MCP SDK + FastAPI + SQLModel)
- [x] Performance requirements are achievable (< 500ms tool execution)
- [x] Security requirements are achievable (user isolation + input validation)

### Gate 3: Resource Availability
- [x] Required technologies are available (MCP SDK, FastAPI, SQLModel, Neon)
- [x] Required infrastructure is available (Neon PostgreSQL)
- [x] Required skills are available (Python, FastAPI, MCP, database design)
- [x] Timeline is realistic (hackathon scope with phased implementation)

## Phase 0: Outline & Research

**Research Tasks:**

1. **MCP SDK Integration Patterns**
   - Research Official MCP SDK for Python
   - Investigate tool registration mechanisms
   - Understand HTTP transport implementation
   - Explore schema definition patterns
   - Study error handling conventions

2. **Tool Naming Conventions and Versioning**
   - Research MCP tool naming best practices
   - Evaluate versioning strategies (v1 prefix, semantic versioning)
   - Determine naming pattern (snake_case vs camelCase)
   - Define tool description format

3. **Error Response Format Standardization**
   - Research MCP error response conventions
   - Design consistent error structure (status, message, details)
   - Define error codes for common scenarios
   - Plan error message templates

4. **Transaction Strategy for Neon DB**
   - Research SQLModel transaction patterns
   - Evaluate transaction isolation levels
   - Determine rollback strategies
   - Plan connection pooling configuration

5. **Logging and Observability Design**
   - Research structured logging formats
   - Design log schema (tool name, parameters, result, duration)
   - Determine log levels (DEBUG, INFO, ERROR)
   - Plan metrics collection (tool invocation counts, latencies)

**Deliverables:**
- research.md (consolidates findings and decisions)

## Phase 1: Design & Contracts

**Design Deliverables:**

### 1. data-model.md

**Entities:**

**Task**
- `id`: Integer (primary key, auto-increment) or UUID
- `user_id`: String (indexed, non-empty)
- `title`: String (1-200 characters, non-empty)
- `description`: String (max 2000 characters, nullable)
- `status`: Enum['pending', 'completed'] (default: pending)
- `due_date`: DateTime (nullable, ISO 8601)
- `created_at`: DateTime (auto-generated, indexed)
- `updated_at`: DateTime (auto-updated)

**Relationships:**
- None (single entity model for hackathon scope)

**Indexes:**
- Primary: id
- Secondary: user_id, created_at (for user task listing)
- Composite: (user_id, status) for filtered queries

**Validation Rules:**
- user_id: non-empty string, max 255 characters
- title: non-empty string, 1-200 characters
- description: string, max 2000 characters if provided
- status: must be 'pending' or 'completed'
- due_date: ISO 8601 format if provided
- created_at: auto-generated, immutable
- updated_at: auto-updated on modifications

---

### 2. contracts/ (Tool Schemas)

**add_task Tool**

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

**Output Schema (Error):**
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
        "code": {"type": "string"},
        "message": {"type": "string"},
        "details": {"type": "object"}
      }
    }
  }
}
```

---

**list_tasks Tool**

**Input Schema:**
```json
{
  "type": "object",
  "required": ["user_id"],
  "properties": {
    "user_id": {
      "type": "string",
      "minLength": 1,
      "maxLength": 255
    },
    "status": {
      "type": "string",
      "enum": ["pending", "completed", "all"],
      "default": "all"
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

---

**complete_task Tool**

**Input Schema:**
```json
{
  "type": "object",
  "required": ["user_id", "task_id"],
  "properties": {
    "user_id": {"type": "string", "minLength": 1, "maxLength": 255},
    "task_id": {"type": "integer", "minimum": 1}
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

---

**delete_task Tool**

**Input Schema:**
```json
{
  "type": "object",
  "required": ["user_id", "task_id"],
  "properties": {
    "user_id": {"type": "string", "minLength": 1, "maxLength": 255},
    "task_id": {"type": "integer", "minimum": 1}
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

---

**update_task Tool**

**Input Schema:**
```json
{
  "type": "object",
  "required": ["user_id", "task_id"],
  "properties": {
    "user_id": {"type": "string", "minLength": 1, "maxLength": 255},
    "task_id": {"type": "integer", "minimum": 1},
    "title": {"type": "string", "minLength": 1, "maxLength": 200},
    "description": {"type": "string", "maxLength": 2000},
    "due_date": {"type": "string", "format": "date-time"}
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

---

### 3. quickstart.md

**Setup Instructions:**

1. **Prerequisites**
   - Python 3.11+
   - Neon PostgreSQL database URL
   - MCP SDK installed

2. **Environment Variables**
   ```
   DATABASE_URL=postgresql://...
   MCP_SERVER_PORT=8001
   LOG_LEVEL=INFO
   ```

3. **Installation**
   ```bash
   pip install fastapi uvicorn sqlmodel psycopg2-binary python-dotenv mcp-sdk
   ```

4. **Database Migration**
   ```bash
   python -m backend.mcp.db.migrate
   ```

5. **Run MCP Server**
   ```bash
   uvicorn backend.mcp.server:app --port 8001
   ```

6. **Test Tool Invocation**
   ```bash
   curl -X POST http://localhost:8001/tools/add_task \
     -H "Content-Type: application/json" \
     -d '{"user_id": "user123", "title": "Test task"}'
   ```

---

**Implementation Approach:**

1. **Database Layer First**
   - Define SQLModel Task model
   - Create database migration scripts
   - Implement CRUD helper functions
   - Add indexes for performance

2. **Tool Schemas Second**
   - Define Pydantic models for input/output schemas
   - Create schema validation decorators
   - Implement error response builders

3. **Tool Handlers Third**
   - Implement 5 tool handler functions
   - Add schema validation
   - Implement database operations
   - Add error handling

4. **MCP Server Fourth**
   - Initialize MCP SDK server
   - Register tools with schemas
   - Configure HTTP transport
   - Add logging and metrics

5. **Integration Fifth**
   - Test tool invocations directly
   - Integrate with AI agent (Spec 2)
   - Validate end-to-end flow
   - Test user isolation

## Phase 2: Implementation Plan

**Tasks:**

### Task Group 1: Database Model & Infrastructure (Foundation)
1. **Define SQLModel Task model**
   - Dependencies: None
   - Priority: P0 (blocking)

2. **Create database migration scripts**
   - Dependencies: Task 1
   - Priority: P0 (blocking)

3. **Implement database connection pooling**
   - Dependencies: Task 1
   - Priority: P0 (blocking)

4. **Add database indexes**
   - Dependencies: Task 2
   - Priority: P1 (performance)

### Task Group 2: Tool Schemas (Contracts)
5. **Define Pydantic input/output schemas for all 5 tools**
   - Dependencies: None
   - Priority: P0 (blocking)

6. **Create schema validation decorators**
   - Dependencies: Task 5
   - Priority: P0 (blocking)

7. **Implement error response builders**
   - Dependencies: Task 5
   - Priority: P0 (blocking)

### Task Group 3: CRUD Operations (Data Access)
8. **Implement add_task handler**
   - create_task(user_id, title, description, due_date) → Task
   - Dependencies: Task 1, 5, 6
   - Priority: P0 (blocking)

9. **Implement list_tasks handler**
   - list_tasks(user_id, status) → List[Task]
   - Dependencies: Task 1, 5, 6
   - Priority: P0 (blocking)

10. **Implement complete_task handler**
    - complete_task(user_id, task_id) → Task
    - Dependencies: Task 1, 5, 6
    - Priority: P0 (blocking)

11. **Implement delete_task handler**
    - delete_task(user_id, task_id) → success message
    - Dependencies: Task 1, 5, 6
    - Priority: P0 (blocking)

12. **Implement update_task handler**
    - update_task(user_id, task_id, **updates) → Task
    - Dependencies: Task 1, 5, 6
    - Priority: P0 (blocking)

### Task Group 4: MCP Server (Integration)
13. **Initialize MCP SDK server**
    - Configure FastAPI integration
    - Set up HTTP transport
    - Dependencies: None
    - Priority: P0 (blocking)

14. **Register tools with MCP server**
    - Register all 5 tools with schemas
    - Dependencies: Task 8-12, 13
    - Priority: P0 (blocking)

15. **Implement tool invocation endpoint**
    - POST /tools/{tool_name}
    - Dependencies: Task 13, 14
    - Priority: P0 (blocking)

16. **Add structured logging**
    - Log tool invocations, parameters, results
    - Dependencies: Task 15
    - Priority: P1 (observability)

17. **Add error handling middleware**
    - Catch and format all errors
    - Dependencies: Task 7, 15
    - Priority: P0 (robustness)

### Task Group 5: Validation & Testing (Quality Assurance)
18. **Test add_task tool**
    - Direct invocation tests
    - Schema validation tests
    - Dependencies: Task 8
    - Priority: P0 (blocking)

19. **Test list_tasks tool**
    - Empty list, filtered list tests
    - Dependencies: Task 9
    - Priority: P0 (blocking)

20. **Test complete_task tool**
    - Success and error cases
    - Dependencies: Task 10
    - Priority: P0 (blocking)

21. **Test delete_task tool**
    - Success and error cases
    - Dependencies: Task 11
    - Priority: P0 (blocking)

22. **Test update_task tool**
    - Partial update tests
    - Dependencies: Task 12
    - Priority: P0 (blocking)

23. **Test user isolation**
    - Cross-user access attempts
    - Dependencies: Task 8-12
    - Priority: P0 (security)

24. **Test agent-to-tool integration**
    - End-to-end flow with AI agent
    - Dependencies: Task 14, 15
    - Priority: P0 (integration)

**Task Dependencies Visualization:**
```
Foundation: [1] → [2] → [3], [4]
Schemas: [5] → [6], [7]
CRUD: [1,5,6] → [8], [9], [10], [11], [12]
MCP Server: [13] → [14] → [15] → [16], [17]
Testing: [8-12] → [18-23], [14,15] → [24]
```

**Priority Order:**
1. P0 (Blocking): Tasks 1-3, 5-15, 17-24
2. P1 (Important): Tasks 4, 16

## Phase 3: Validation & Testing

**Validation Approach:**

### 1. Functional Validation
- **Tool Implementation**: Verify all 5 tools implemented with correct parameters
- **Schema Validation**: Test input/output validation for all tools
- **Database Persistence**: Verify all operations persisted correctly
- **User Isolation**: Confirm users cannot access others' tasks
- **Error Handling**: Test all error scenarios return structured responses

### 2. Performance Validation
- **Tool Execution Time**: Measure execution time for each tool (target < 500ms)
- **Concurrent Invocations**: Test 10 concurrent tool calls
- **Database Query Performance**: Verify indexes improve query speed

### 3. Security Validation
- **User Isolation**: Attempt cross-user access, verify failures
- **Input Validation**: Send invalid inputs, verify rejections
- **SQL Injection**: Attempt SQL injection, verify parameterized queries prevent

### 4. Integration Validation
- **MCP Protocol**: Verify tools invocable via MCP protocol
- **Agent Integration**: Test AI agent can invoke all tools
- **End-to-End Flow**: Complete user scenario from agent to database

**Testing Strategy:**

### Unit Tests
- Task model validation
- CRUD helper functions
- Schema validation decorators
- Error response builders

### Integration Tests
- Tool handlers with mocked database
- MCP server with mocked tools
- Database operations with test database

### End-to-End Tests
- Complete tool invocation flow
- Agent-to-tool-to-database flow
- User isolation scenarios
- Error handling scenarios

**Success Criteria:**

1. ✅ **Tool Implementation Completeness**: All 5 tools implemented with required parameters
2. ✅ **Schema Validation**: 100% of invocations validated against schemas
3. ✅ **Database Persistence**: 100% of operations persisted and retrievable
4. ✅ **MCP Protocol Compliance**: Agent successfully invokes all tools via MCP
5. ✅ **Error Handling Quality**: All error scenarios return structured responses
6. ✅ **User Isolation**: Zero cross-user data access in security tests
7. ✅ **Stateless Execution**: Tools invocable from multiple instances without conflicts

## Architectural Decisions

### Decision 1: Tool Naming Conventions and Versioning

**Decision**: Use snake_case naming without version prefix for hackathon scope

**Rationale**:
- snake_case aligns with Python conventions
- No versioning needed for hackathon (single version)
- Simple names improve readability (add_task vs addTask or add_task_v1)
- Can add versioning later if needed (add_task_v2)

**Tool Names**:
- add_task
- list_tasks
- complete_task
- delete_task
- update_task

**Future Versioning Strategy**:
- If breaking changes needed: add_task_v2
- If minor changes: update existing tool (backward compatible)
- Document version in tool description

### Decision 2: Error Response Format Standardization

**Decision**: Consistent error structure with status, code, message, and optional details

**Error Response Format**:
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

**Error Codes**:
- `VALIDATION_ERROR`: Input validation failed
- `TASK_NOT_FOUND`: Task doesn't exist or user doesn't have access
- `DATABASE_ERROR`: Database operation failed
- `INTERNAL_ERROR`: Unexpected error

**Rationale**:
- Consistent structure enables reliable error handling
- Error codes enable programmatic error handling
- Human-readable messages help debugging
- Details provide context without leaking internals

### Decision 3: Transaction Strategy for Neon DB

**Decision**: Use SQLModel session with automatic transaction management per tool invocation

**Implementation**:
```python
def tool_handler(user_id, ...):
    with Session(engine) as session:
        # All operations in this block are transactional
        task = Task(user_id=user_id, ...)
        session.add(task)
        session.commit()
        session.refresh(task)
        return task
```

**Rationale**:
- SQLModel provides automatic transaction management
- Context manager ensures proper cleanup
- Commit on success, rollback on exception
- Simple pattern for hackathon scope

**Transaction Isolation**:
- Use default isolation level (READ COMMITTED)
- Sufficient for hackathon scope
- Can upgrade to SERIALIZABLE if needed

**Connection Pooling**:
- Use SQLModel's built-in connection pooling
- Configure pool size based on expected load
- Set reasonable timeout for connection acquisition

### Decision 4: Logging and Observability Design

**Decision**: Structured logging with JSON format for tool invocations

**Log Format**:
```json
{
  "timestamp": "2026-02-09T10:30:00Z",
  "level": "INFO",
  "tool_name": "add_task",
  "user_id": "user123",
  "parameters": {"title": "Test task"},
  "result": "success",
  "duration_ms": 45,
  "task_id": 456
}
```

**Log Levels**:
- DEBUG: Detailed execution flow
- INFO: Tool invocations and results
- WARNING: Validation failures, not-found errors
- ERROR: Database errors, unexpected exceptions

**Metrics to Collect**:
- Tool invocation counts (by tool name)
- Tool execution latencies (p50, p95, p99)
- Error rates (by error code)
- Database query times

**Rationale**:
- Structured logs enable easy parsing and analysis
- JSON format works with log aggregation tools
- Metrics enable performance monitoring
- Separate log levels enable filtering

## Risk Mitigation

### Risk 1: MCP SDK Integration Complexity
- **Mitigation**: Research MCP SDK early, create proof-of-concept
- **Fallback**: Implement minimal MCP protocol manually if SDK issues

### Risk 2: Schema Validation Overhead
- **Mitigation**: Use efficient Pydantic validation, cache schemas
- **Monitoring**: Profile validation performance

### Risk 3: Database Connection Failures
- **Mitigation**: Implement retry logic, use connection pooling
- **Monitoring**: Log all database errors

### Risk 4: User Isolation Bugs
- **Mitigation**: Comprehensive testing, code review on query filters
- **Validation**: Automated security tests

### Risk 5: Tool Schema Evolution
- **Mitigation**: Define schemas early, document clearly
- **Communication**: Coordinate with agent team on changes

## Next Steps

1. **Phase 0 Complete**: Create research.md with MCP SDK findings
2. **Phase 1 Complete**: Create data-model.md, contracts/, and quickstart.md
3. **Proceed to Tasks**: Run `/sp.tasks` to generate detailed task breakdown
4. **Implementation**: Execute tasks in priority order (P0 first)
5. **Validation**: Run test suite and verify success criteria
6. **Integration**: Connect with AI agent (Spec 2) for end-to-end testing
