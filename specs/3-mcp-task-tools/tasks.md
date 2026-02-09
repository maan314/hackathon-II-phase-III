# Implementation Tasks: MCP Server and Task Tooling System

**Feature:** 3-mcp-task-tools
**Branch:** 3-mcp-task-tools
**Spec:** specs/3-mcp-task-tools/spec.md
**Plan:** specs/3-mcp-task-tools/plan.md

## Overview

This document provides a detailed, executable task breakdown for implementing the MCP Server and Task Tooling System. Tasks are organized by user story to enable independent implementation and testing.

**Total Tasks:** 52
**Parallelization Opportunities:** 18 tasks marked with [P]
**User Stories:** 5 core tools (add_task, list_tasks, complete_task, delete_task, update_task)

## Implementation Strategy

**MVP Scope:** US1 (add_task tool) + Foundational infrastructure
**Incremental Delivery:** One tool per iteration, each independently testable
**Parallel Execution:** Tasks marked [P] can run concurrently within each phase

---

## Phase 1: Setup & Project Initialization

**Goal:** Establish project structure, dependencies, and environment configuration

**Tasks:**

- [ ] T001 Create backend/mcp directory structure (server.py, tools/, db/, schemas/)
- [ ] T002 Create requirements.txt with dependencies (fastapi, uvicorn, sqlmodel, psycopg2-binary, python-dotenv, mcp-sdk)
- [ ] T003 Create .env.example file with DATABASE_URL, MCP_SERVER_PORT, LOG_LEVEL placeholders
- [ ] T004 Create backend/mcp/__init__.py to mark as Python package
- [ ] T005 [P] Create backend/mcp/config.py for environment variable loading using python-dotenv
- [ ] T006 [P] Create backend/mcp/db/__init__.py for database module initialization

**Acceptance Criteria:**
- Project structure matches plan.md specifications
- All dependencies installable via pip install -r requirements.txt
- Environment configuration loads correctly from .env file

---

## Phase 2: Foundational Infrastructure

**Goal:** Implement shared components required by all tools (database, schemas, MCP server)

### Database Layer

- [ ] T007 Define TaskStatus enum (PENDING, COMPLETED) in backend/mcp/db/models.py
- [ ] T008 Define Task SQLModel class with all fields (id, user_id, title, description, status, due_date, created_at, updated_at) in backend/mcp/db/models.py
- [ ] T009 Create database engine with connection pooling (pool_size=10, max_overflow=20) in backend/mcp/db/engine.py
- [ ] T010 Create database migration script (001_create_tasks_table.sql) in backend/mcp/db/migrations/
- [ ] T011 Create migration runner (migrate.py) that executes SQL migrations in backend/mcp/db/
- [ ] T012 [P] Create database seed script (seed.py) for test data in backend/mcp/db/

### Schema Validation Layer

- [ ] T013 Create ToolError exception class (code, message, details) in backend/mcp/schemas/errors.py
- [ ] T014 Create format_error_response function in backend/mcp/schemas/errors.py
- [ ] T015 [P] Create AddTaskInput Pydantic schema in backend/mcp/schemas/inputs.py
- [ ] T016 [P] Create ListTasksInput Pydantic schema in backend/mcp/schemas/inputs.py
- [ ] T017 [P] Create CompleteTaskInput Pydantic schema in backend/mcp/schemas/inputs.py
- [ ] T018 [P] Create DeleteTaskInput Pydantic schema in backend/mcp/schemas/inputs.py
- [ ] T019 [P] Create UpdateTaskInput Pydantic schema in backend/mcp/schemas/inputs.py
- [ ] T020 [P] Create TaskResponse Pydantic schema in backend/mcp/schemas/outputs.py
- [ ] T021 [P] Create TaskListResponse Pydantic schema in backend/mcp/schemas/outputs.py
- [ ] T022 [P] Create SuccessResponse and ErrorResponse schemas in backend/mcp/schemas/outputs.py

### MCP Server Setup

- [ ] T023 Initialize MCPServer instance in backend/mcp/server.py
- [ ] T024 Create FastAPI app and integrate MCP server router in backend/mcp/server.py
- [ ] T025 [P] Add health check endpoint (GET /health) in backend/mcp/server.py
- [ ] T026 [P] Add tools list endpoint (GET /tools) in backend/mcp/server.py
- [ ] T027 Configure structured logging with JSON format in backend/mcp/logging_config.py

**Acceptance Criteria:**
- Database migration creates tasks table with all indexes
- All input/output schemas validate correctly
- MCP server starts without errors
- Health check returns 200 OK

**Independent Test:**
```bash
# Run migration
python -m backend.mcp.db.migrate

# Start server
uvicorn backend.mcp.server:app --port 8001

# Test health check
curl http://localhost:8001/health
```

---

## Phase 3: US1 - add_task Tool

**Goal:** Implement tool to create new tasks with validation and persistence

**User Story:** As an AI agent, I want to create tasks for users so that I can help them manage their todo list.

### Implementation Tasks

- [ ] T028 [US1] Create create_task CRUD function in backend/mcp/db/crud.py (accepts user_id, title, description, due_date; returns Task)
- [ ] T029 [US1] Implement add_task tool handler in backend/mcp/tools/add_task.py with schema validation
- [ ] T030 [US1] Register add_task tool with MCP server using @mcp_server.tool decorator in backend/mcp/server.py
- [ ] T031 [US1] Add structured logging for add_task invocations in backend/mcp/tools/add_task.py
- [ ] T032 [US1] Implement error handling for validation failures and database errors in backend/mcp/tools/add_task.py

### Testing Tasks

- [ ] T033 [US1] Test add_task with valid inputs (title only, title + description, title + due_date, all fields)
- [ ] T034 [US1] Test add_task validation errors (empty title, title > 200 chars, description > 2000 chars, invalid due_date format)
- [ ] T035 [US1] Test add_task database persistence (verify task created in database with correct values)
- [ ] T036 [US1] Test add_task returns correct response schema (status: success, task object with all fields)

**Acceptance Criteria:**
- Tool creates tasks in database with user_id isolation
- Input validation rejects invalid parameters
- Returns structured success response with task details
- Errors return structured error response

**Independent Test:**
```bash
curl -X POST http://localhost:8001/tools/add_task \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user123", "title": "Test task", "description": "Test description"}'
```

**Expected Output:**
```json
{
  "status": "success",
  "task": {
    "id": 1,
    "user_id": "user123",
    "title": "Test task",
    "description": "Test description",
    "status": "pending",
    "due_date": null,
    "created_at": "2026-02-09T10:30:00Z",
    "updated_at": "2026-02-09T10:30:00Z"
  }
}
```

---

## Phase 4: US2 - list_tasks Tool

**Goal:** Implement tool to retrieve user's tasks with optional status filtering

**User Story:** As an AI agent, I want to list a user's tasks so that I can show them their current todo items.

### Implementation Tasks

- [ ] T037 [US2] Create list_tasks CRUD function in backend/mcp/db/crud.py (accepts user_id, status filter; returns List[Task])
- [ ] T038 [US2] Implement list_tasks tool handler in backend/mcp/tools/list_tasks.py with schema validation
- [ ] T039 [US2] Register list_tasks tool with MCP server in backend/mcp/server.py
- [ ] T040 [US2] Add structured logging for list_tasks invocations in backend/mcp/tools/list_tasks.py
- [ ] T041 [US2] Implement query optimization with LIMIT 100 and proper index usage in backend/mcp/db/crud.py

### Testing Tasks

- [ ] T042 [US2] Test list_tasks with no filter (returns all tasks for user)
- [ ] T043 [US2] Test list_tasks with status=pending filter
- [ ] T044 [US2] Test list_tasks with status=completed filter
- [ ] T045 [US2] Test list_tasks returns empty array for user with no tasks
- [ ] T046 [US2] Test list_tasks user isolation (user A cannot see user B's tasks)

**Acceptance Criteria:**
- Tool retrieves only tasks belonging to specified user_id
- Status filter works correctly (pending, completed, all)
- Returns empty array (not error) when no tasks found
- Results ordered by created_at descending

**Independent Test:**
```bash
curl -X POST http://localhost:8001/tools/list_tasks \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user123", "status": "pending"}'
```

---

## Phase 5: US3 - complete_task Tool

**Goal:** Implement tool to mark tasks as completed

**User Story:** As an AI agent, I want to mark tasks as completed so that users can track their progress.

### Implementation Tasks

- [ ] T047 [US3] Create complete_task CRUD function in backend/mcp/db/crud.py (accepts user_id, task_id; returns updated Task)
- [ ] T048 [US3] Implement complete_task tool handler in backend/mcp/tools/complete_task.py with user isolation
- [ ] T049 [US3] Register complete_task tool with MCP server in backend/mcp/server.py
- [ ] T050 [US3] Add structured logging for complete_task invocations in backend/mcp/tools/complete_task.py
- [ ] T051 [US3] Implement idempotent behavior (completing already-completed task succeeds) in backend/mcp/tools/complete_task.py

### Testing Tasks

- [ ] T052 [US3] Test complete_task with valid task_id (status changes to completed, updated_at changes)
- [ ] T053 [US3] Test complete_task with non-existent task_id (returns TASK_NOT_FOUND error)
- [ ] T054 [US3] Test complete_task user isolation (user A cannot complete user B's task)
- [ ] T055 [US3] Test complete_task idempotency (completing already-completed task succeeds)

**Acceptance Criteria:**
- Tool updates task status to completed
- Updates updated_at timestamp
- Enforces user isolation (task_id + user_id filter)
- Returns TASK_NOT_FOUND for invalid task_id or wrong user_id

**Independent Test:**
```bash
curl -X POST http://localhost:8001/tools/complete_task \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user123", "task_id": 1}'
```

---

## Phase 6: US4 - delete_task Tool

**Goal:** Implement tool to permanently remove tasks

**User Story:** As an AI agent, I want to delete tasks so that users can remove items they no longer need.

### Implementation Tasks

- [ ] T056 [US4] Create delete_task CRUD function in backend/mcp/db/crud.py (accepts user_id, task_id; returns bool)
- [ ] T057 [US4] Implement delete_task tool handler in backend/mcp/tools/delete_task.py with user isolation
- [ ] T058 [US4] Register delete_task tool with MCP server in backend/mcp/server.py
- [ ] T059 [US4] Add structured logging for delete_task invocations in backend/mcp/tools/delete_task.py

### Testing Tasks

- [ ] T060 [US4] Test delete_task with valid task_id (task removed from database)
- [ ] T061 [US4] Test delete_task with non-existent task_id (returns TASK_NOT_FOUND error)
- [ ] T062 [US4] Test delete_task user isolation (user A cannot delete user B's task)
- [ ] T063 [US4] Test delete_task returns success message with task_id

**Acceptance Criteria:**
- Tool permanently deletes task from database
- Enforces user isolation (task_id + user_id filter)
- Returns TASK_NOT_FOUND for invalid task_id or wrong user_id
- Returns success message with deleted task_id

**Independent Test:**
```bash
curl -X POST http://localhost:8001/tools/delete_task \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user123", "task_id": 1}'
```

---

## Phase 7: US5 - update_task Tool

**Goal:** Implement tool to modify task attributes (partial updates)

**User Story:** As an AI agent, I want to update task details so that users can modify their todo items.

### Implementation Tasks

- [ ] T064 [US5] Create update_task CRUD function in backend/mcp/db/crud.py (accepts user_id, task_id, **updates; returns updated Task)
- [ ] T065 [US5] Implement update_task tool handler in backend/mcp/tools/update_task.py with partial update support
- [ ] T066 [US5] Register update_task tool with MCP server in backend/mcp/server.py
- [ ] T067 [US5] Add structured logging for update_task invocations in backend/mcp/tools/update_task.py
- [ ] T068 [US5] Implement validation for optional fields (title, description, due_date) in backend/mcp/tools/update_task.py

### Testing Tasks

- [ ] T069 [US5] Test update_task with single field update (title only)
- [ ] T070 [US5] Test update_task with multiple field updates (title + description + due_date)
- [ ] T071 [US5] Test update_task with non-existent task_id (returns TASK_NOT_FOUND error)
- [ ] T072 [US5] Test update_task user isolation (user A cannot update user B's task)
- [ ] T073 [US5] Test update_task validation (empty title, title > 200 chars, description > 2000 chars)

**Acceptance Criteria:**
- Tool updates only provided fields (partial update)
- Updates updated_at timestamp
- Enforces user isolation (task_id + user_id filter)
- Validates updated fields against constraints

**Independent Test:**
```bash
curl -X POST http://localhost:8001/tools/update_task \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user123", "task_id": 1, "title": "Updated title", "due_date": "2026-02-20T17:00:00Z"}'
```

---

## Phase 8: Integration, Testing & Polish

**Goal:** Ensure all tools work together, handle errors gracefully, and meet performance requirements

### Integration Tasks

- [ ] T074 Test end-to-end flow: add_task → list_tasks → complete_task → list_tasks (verify completed)
- [ ] T075 Test end-to-end flow: add_task → update_task → delete_task (verify deleted)
- [ ] T076 Test concurrent tool invocations (10 simultaneous add_task calls from different users)
- [ ] T077 Test user isolation across all tools (create comprehensive security test suite)

### Error Handling Tasks

- [ ] T078 [P] Test database connection failure handling (mock connection error, verify graceful error response)
- [ ] T079 [P] Test transaction rollback on error (start transaction, trigger error, verify no partial state)
- [ ] T080 [P] Verify all error responses follow consistent format (status, error.code, error.message, error.details)

### Performance Tasks

- [ ] T081 Measure tool execution times (target < 500ms for single task operations)
- [ ] T082 Verify database indexes improve query performance (run EXPLAIN on list_tasks query)
- [ ] T083 Test list_tasks performance with 100 tasks (should complete < 1 second)

### Documentation Tasks

- [ ] T084 [P] Create API documentation with tool schemas in docs/api.md
- [ ] T085 [P] Create deployment guide in docs/deployment.md
- [ ] T086 [P] Update README.md with quickstart instructions

### Polish Tasks

- [ ] T087 Add request_id to all log entries for request tracing in backend/mcp/logging_config.py
- [ ] T088 Add metrics collection (tool invocation counts, latencies) in backend/mcp/metrics.py
- [ ] T089 Configure CORS for frontend integration in backend/mcp/server.py
- [ ] T090 Add rate limiting middleware (optional, if time permits) in backend/mcp/middleware.py

**Acceptance Criteria:**
- All 5 tools work correctly in isolation and together
- User isolation enforced across all operations
- Error handling is consistent and informative
- Performance meets targets (< 500ms per operation)
- Documentation is complete and accurate

**Final Integration Test:**
```bash
# Test complete workflow
curl -X POST http://localhost:8001/tools/add_task -d '{"user_id": "user123", "title": "Task 1"}'
curl -X POST http://localhost:8001/tools/list_tasks -d '{"user_id": "user123", "status": "all"}'
curl -X POST http://localhost:8001/tools/complete_task -d '{"user_id": "user123", "task_id": 1}'
curl -X POST http://localhost:8001/tools/update_task -d '{"user_id": "user123", "task_id": 1, "title": "Updated Task 1"}'
curl -X POST http://localhost:8001/tools/delete_task -d '{"user_id": "user123", "task_id": 1}'
```

---

## Task Dependencies

### Dependency Graph

```
Phase 1 (Setup)
  T001-T006 → Phase 2

Phase 2 (Foundational)
  Database: T007 → T008 → T009 → T010 → T011
  Schemas: T013 → T014, T015-T022 (parallel)
  MCP Server: T023 → T024 → T025, T026 (parallel)

  Phase 2 Complete → Phase 3, 4, 5, 6, 7 (parallel)

Phase 3 (US1 - add_task)
  T028 → T029 → T030 → T031, T032
  T030 → T033-T036 (testing)

Phase 4 (US2 - list_tasks)
  T037 → T038 → T039 → T040, T041
  T039 → T042-T046 (testing)

Phase 5 (US3 - complete_task)
  T047 → T048 → T049 → T050, T051
  T049 → T052-T055 (testing)

Phase 6 (US4 - delete_task)
  T056 → T057 → T058 → T059
  T058 → T060-T063 (testing)

Phase 7 (US5 - update_task)
  T064 → T065 → T066 → T067, T068
  T066 → T069-T073 (testing)

Phase 8 (Integration & Polish)
  Phases 3-7 Complete → T074-T090
```

### Parallel Execution Opportunities

**Phase 1:** T005, T006 can run in parallel
**Phase 2:** T015-T022 (all schema definitions), T025-T026 can run in parallel
**Phase 3-7:** All user story phases can run in parallel after Phase 2 completes
**Phase 8:** T078-T080, T084-T086 can run in parallel

---

## MVP Scope

**Minimum Viable Product includes:**
- Phase 1: Setup (T001-T006)
- Phase 2: Foundational (T007-T027)
- Phase 3: US1 - add_task tool (T028-T036)
- Phase 4: US2 - list_tasks tool (T037-T046)

**MVP Deliverable:** Working MCP server with 2 tools (add and list tasks) that demonstrates:
- Tool registration and invocation
- Schema validation
- Database persistence
- User isolation
- Error handling

**Estimated MVP Tasks:** 46 tasks (T001-T046)
**Full Feature Tasks:** 90 tasks (T001-T090)

---

## Success Metrics

### Functional Completeness
- [ ] All 5 tools implemented and registered
- [ ] All tools validate inputs against schemas
- [ ] All tools persist operations to database
- [ ] All tools enforce user isolation

### Quality Metrics
- [ ] 100% of tool invocations validated against schemas
- [ ] 100% of operations persisted to database
- [ ] Zero cross-user data access in security tests
- [ ] All error scenarios return structured responses

### Performance Metrics
- [ ] Tool execution time < 500ms (p95)
- [ ] list_tasks with 100 tasks < 1 second
- [ ] Concurrent invocations supported without conflicts

### Integration Metrics
- [ ] Agent successfully invokes all tools via MCP protocol
- [ ] End-to-end flows complete successfully
- [ ] Tools work correctly from multiple server instances

---

## Notes

- **Tests are optional:** Test tasks (T033-T036, T042-T046, etc.) should be implemented if time permits or if TDD approach is preferred
- **Parallelization:** Tasks marked [P] can be executed concurrently to speed up development
- **User Story Independence:** Each user story (US1-US5) can be implemented independently after Phase 2 completes
- **Incremental Delivery:** Each phase produces a testable increment that can be demonstrated
- **File Paths:** All file paths are specified in task descriptions for clarity
