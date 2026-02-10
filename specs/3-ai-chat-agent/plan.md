# Implementation Plan: AI Chat Agent and Conversation System

## Feature Context

**Feature:** AI Chat Agent and Conversation System
**Branch:** 3-ai-chat-agent
**Spec:** specs/3-ai-chat-agent/spec.md

## Technical Context

**Architecture:**
- Three-tier stateless architecture:
  - API Layer: FastAPI endpoint handling HTTP requests
  - Agent Layer: Cohere API processing natural language and invoking tools
  - Data Layer: Neon PostgreSQL storing conversations, messages, and tasks
- Request flow: HTTP → Auth Middleware → Chat Endpoint → Load Conversation → Agent Processing → Tool Invocation → Persist Message → Response
- Stateless design: Each request reconstructs context from database

**Technologies:**
- Backend Framework: FastAPI (Python)
- AI Agent: Cohere API
- ORM: SQLModel
- Database: Neon PostgreSQL
- Authentication: Better Auth with JWT
- MCP Integration: Official MCP SDK for tool server
- Tools: add_task, list_tasks, complete_task, delete_task, update_task (already implemented)

**Infrastructure:**
- Database: Neon PostgreSQL (serverless, already configured)
- API Server: FastAPI application (existing backend)
- Cohere API: External service for agent processing
- Environment: Development and production configurations via .env

**Security:**
- JWT-based authentication with user_id extraction
- User isolation enforced at database query level
- Input validation on all endpoints
- Tool invocations include user_id for task isolation
- Conversation access restricted to owning user
- HTTPS for all communications
- Database credentials in environment variables

## Constitution Check

**Principles Applied:**

✅ **Principle 1: Stateless Server Architecture with Persistent Conversation Storage**
- Implementation: All conversation state persisted in Neon PostgreSQL
- Verification: No in-memory session storage; conversation history loaded per request
- Compliance: Chat endpoint retrieves conversation from DB on each request

✅ **Principle 2: Tool-Driven AI Behavior**
- Implementation: Agent uses MCP tools exclusively for task operations
- Verification: No direct database writes from agent; all mutations via tools
- Compliance: Agent configured with MCP tool definitions only

✅ **Principle 3: Deterministic Agent Execution via OpenAI Agents SDK**
- Implementation: OpenAI Agents SDK with defined system prompt
- Verification: Consistent agent behavior for identical inputs and conversation states
- Compliance: System prompt defines deterministic tool selection rules

✅ **Principle 4: Traceable Conversation Logs for Auditability**
- Implementation: All messages and tool invocations logged to database
- Verification: Structured logging for tool_calls, responses, timestamps
- Compliance: Message model includes role, content, timestamp, metadata

✅ **Principle 5: Natural Language to Structured Tool Invocation**
- Implementation: Agent interprets natural language and invokes MCP tools
- Verification: User messages → Agent processing → Tool calls with parameters
- Compliance: Agent system prompt includes tool usage examples

✅ **Principle 6: Tools as Exclusive Interface for Task Mutation**
- Implementation: All task operations via MCP tools (add, list, update, complete, delete)
- Verification: No alternative mutation paths; agent cannot directly modify tasks
- Compliance: Agent has no database access; only tool invocation capability

✅ **Principle 7: Stateless MCP Server with Database Persistence**
- Implementation: MCP tools retrieve and persist task data per invocation
- Verification: No in-memory state in MCP server between tool calls
- Compliance: Tools implemented with database queries per invocation

✅ **Principle 8: Tool Schema Strict Validation**
- Implementation: MCP tool schemas define input/output structures
- Verification: Tool parameters validated against JSON schemas
- Compliance: Agent SDK validates tool calls against registered schemas

✅ **Principle 9: Agent-Tool Separation of Concerns**
- Implementation: Agent handles NLP; tools handle CRUD operations
- Verification: Tools contain no AI logic; agent contains no direct DB access
- Compliance: Clear boundary between agent reasoning and tool execution

**Key Standards Compliance:**

✅ **Standard 1: Chat State Persistence** - Conversation and Message models in Neon PostgreSQL
✅ **Standard 2: Agent Interaction via MCP Tools** - Agent configured with MCP tool definitions
✅ **Standard 3: Conversation History Retrieval** - Load messages per request from database
✅ **Standard 4: No In-Memory Session State** - Stateless FastAPI endpoint design
✅ **Standard 5: Structured Logging** - Message metadata includes tool invocations and results
✅ **Standard 6: MCP Tool Schema Compliance** - Tools match existing JSON schemas
✅ **Standard 7: Tool State Persistence** - Tools use SQLModel for database operations
✅ **Standard 8: Pure CRUD Tools** - Existing tools contain only data operations
✅ **Standard 9: Structured Tool Responses** - Tools return status, result, error format

**Constraints Verification:**

✅ **Constraint 1: Backend Framework** - FastAPI + OpenAI Agents SDK
✅ **Constraint 2: ORM and Database** - SQLModel + Neon PostgreSQL
✅ **Constraint 3: Authentication** - Better Auth with user_id enforcement
✅ **Constraint 4: API Endpoint** - POST /api/{user_id}/chat (stateless)
✅ **Constraint 5: MCP SDK Usage** - Official MCP SDK for tool server
✅ **Constraint 6: MCP Tool Set** - add_task, list_tasks, complete_task, delete_task, update_task

**Compliance Status:**
- ✅ All constitutional principles satisfied
- ✅ All key standards met
- ✅ All constraints verified
- ⚠️ Potential consideration: Context window management for long conversations (addressed in research phase)

## Gates

### Gate 1: Requirements Clarity
- [x] All functional requirements are understood (7 requirements with clear acceptance criteria)
- [x] All non-functional requirements are understood (performance, reliability, scalability, maintainability)
- [x] All constraints are understood (FastAPI, SQLModel, Neon, OpenAI Agents SDK, MCP tools)
- [x] All success criteria are understood (7 measurable outcomes defined)

**Status:** ✅ PASSED

### Gate 2: Technical Feasibility
- [x] Architecture supports all requirements (stateless design with DB persistence)
- [x] Technology choices enable required functionality (OpenAI Agents SDK + MCP tools)
- [x] Performance requirements are achievable (5s response time with DB + AI processing)
- [x] Security requirements are achievable (JWT auth, user isolation, input validation)

**Status:** ✅ PASSED

### Gate 3: Resource Availability
- [x] Required technologies are available (OpenAI API, Neon DB, FastAPI, MCP SDK)
- [x] Required infrastructure is available (existing backend, database configured)
- [x] Required skills are available (Python, FastAPI, SQLModel, AI agent integration)
- [x] Timeline is realistic (Phase-III hackathon submission deadline)

**Status:** ✅ PASSED

## Phase 0: Outline & Research

**Research Tasks:**

1. **OpenAI Agents SDK Integration with FastAPI**
   - Research: How to integrate OpenAI Agents SDK into FastAPI endpoints
   - Focus: Async/await patterns, error handling, timeout management
   - Deliverable: Integration pattern and code examples

2. **Agent System Prompt Design**
   - Research: Best practices for system prompts with tool-calling agents
   - Focus: Tool usage instructions, error handling, user confirmation patterns
   - Deliverable: System prompt template with examples

3. **Conversation Context Window Management**
   - Research: Strategies for managing conversation history within token limits
   - Focus: Message truncation, context summarization, sliding window approaches
   - Deliverable: Context management strategy and implementation approach

4. **MCP Tool Integration with OpenAI Agents**
   - Research: How to register MCP tools with OpenAI Agents SDK
   - Focus: Tool schema format, parameter passing, response handling
   - Deliverable: Tool registration pattern and integration code

5. **Database Schema for Conversations**
   - Research: Best practices for conversation and message storage
   - Focus: Indexing strategies, query optimization, relationship modeling
   - Deliverable: Optimized schema design with indexes

**Deliverables:**
- research.md (consolidates all findings with decisions and rationale)

## Phase 1: Design & Contracts

**Design Deliverables:**

### 1. data-model.md
**Entities:**
- Conversation (id, user_id, title, created_at, updated_at, metadata)
- Message (id, conversation_id, role, content, timestamp, tool_calls, metadata)
- Tool invocation tracking (embedded in Message metadata)

**Relationships:**
- Conversation 1:N Messages
- Message references Conversation (foreign key)
- User isolation via user_id on Conversation

**Validation Rules:**
- conversation_id must be UUID format
- role must be "user" or "assistant"
- user_id must match authenticated user
- timestamps must be chronological within conversation

### 2. contracts/
**API Schemas:**
- POST /api/{user_id}/chat
  - Request: ChatRequest (message: str, conversation_id: Optional[str])
  - Response: ChatResponse (response: str, conversation_id: str, message_id: str)
  - Errors: 401 Unauthorized, 400 Bad Request, 403 Forbidden, 500 Internal Server Error

**Tool Schemas:**
- add_task, list_tasks, complete_task, delete_task, update_task (reference existing MCP tool schemas)

### 3. quickstart.md
**Setup Instructions:**
- Environment variables configuration (OPENAI_API_KEY, DATABASE_URL)
- Database migration for Conversation and Message models
- Agent initialization and tool registration
- Testing the chat endpoint with sample requests

**Implementation Approach:**

1. **Database Layer**
   - Create Conversation and Message SQLModel models
   - Add database migrations for new tables
   - Implement repository pattern for conversation/message CRUD
   - Add indexes for user_id and conversation_id queries

2. **Agent Layer**
   - Initialize OpenAI Agents SDK with API key
   - Register MCP tools with agent (add_task, list_tasks, etc.)
   - Define system prompt for task management agent
   - Implement context window management (last N messages)
   - Handle tool invocation results and error responses

3. **API Layer**
   - Create chat endpoint: POST /api/{user_id}/chat
   - Implement authentication middleware (JWT validation)
   - Add request validation (message length, conversation_id format)
   - Implement conversation loading and message persistence
   - Handle agent processing and response generation
   - Add error handling for AI service failures

4. **Integration Layer**
   - Connect agent to MCP tool server
   - Implement tool invocation with user_id injection
   - Handle tool responses and format for agent
   - Log tool invocations in message metadata

## Phase 2: Implementation Plan

**Tasks:**

### Task 1: Database Models and Migrations
**Priority:** P0 (Blocking)
**Dependencies:** None
**Description:**
- Create Conversation SQLModel with fields: id (UUID), user_id (str), title (Optional[str]), created_at (datetime), updated_at (datetime), metadata (JSON)
- Create Message SQLModel with fields: id (UUID), conversation_id (UUID FK), role (str), content (str), timestamp (datetime), tool_calls (Optional[JSON]), metadata (JSON)
- Add database indexes: user_id on Conversation, conversation_id on Message, timestamp on Message
- Create Alembic migration scripts
- Test migrations on local database

**Acceptance Criteria:**
- Models defined with proper types and constraints
- Foreign key relationship between Message and Conversation
- Indexes created for query optimization
- Migration runs successfully without errors

### Task 2: Conversation Repository
**Priority:** P0 (Blocking)
**Dependencies:** Task 1
**Description:**
- Create ConversationRepository class with methods:
  - create_conversation(user_id: str) -> Conversation
  - get_conversation(conversation_id: str, user_id: str) -> Optional[Conversation]
  - list_conversations(user_id: str) -> List[Conversation]
- Create MessageRepository class with methods:
  - add_message(conversation_id: str, role: str, content: str, tool_calls: Optional[dict]) -> Message
  - get_messages(conversation_id: str, limit: int) -> List[Message]
- Implement user_id isolation in all queries
- Add error handling for database operations

**Acceptance Criteria:**
- Repository methods enforce user_id filtering
- Queries are optimized with proper indexes
- Error handling for not found and database errors
- Unit tests for all repository methods

### Task 3: OpenAI Agent Initialization
**Priority:** P0 (Blocking)
**Dependencies:** Research (Task from Phase 0)
**Description:**
- Install OpenAI Agents SDK package
- Create AgentService class to manage agent lifecycle
- Initialize agent with API key from environment
- Define system prompt for task management agent
- Configure agent parameters (model, temperature, max_tokens)
- Implement agent error handling and timeout management

**Acceptance Criteria:**
- Agent initializes successfully with valid API key
- System prompt includes tool usage instructions
- Agent configuration is environment-driven
- Error handling for API failures and timeouts

### Task 4: MCP Tool Registration
**Priority:** P0 (Blocking)
**Dependencies:** Task 3
**Description:**
- Load MCP tool schemas (add_task, list_tasks, complete_task, delete_task, update_task)
- Register tools with OpenAI agent using SDK patterns
- Implement tool invocation handler that:
  - Receives tool call from agent
  - Injects user_id into tool parameters
  - Invokes MCP tool via SDK
  - Returns structured response to agent
- Add logging for tool invocations

**Acceptance Criteria:**
- All 5 MCP tools registered with agent
- Tool schemas match MCP server definitions
- user_id injection works correctly
- Tool invocation logs include parameters and results

### Task 5: Chat Endpoint Implementation
**Priority:** P1 (Critical Path)
**Dependencies:** Task 2, Task 4
**Description:**
- Create POST /api/{user_id}/chat endpoint in FastAPI
- Implement request validation:
  - Validate user_id matches JWT token
  - Validate message is non-empty string
  - Validate conversation_id format (if provided)
- Implement conversation flow:
  - Load or create conversation
  - Retrieve conversation history (last N messages)
  - Prepare context for agent
  - Invoke agent with user message
  - Persist user message and agent response
  - Return response to client
- Add error handling for all failure modes

**Acceptance Criteria:**
- Endpoint accepts valid requests and returns responses
- Authentication enforced (401 for invalid JWT)
- User isolation enforced (403 for wrong user_id)
- Conversation history loaded correctly
- Messages persisted in database
- Error responses include appropriate status codes

### Task 6: Context Window Management
**Priority:** P1 (Critical Path)
**Dependencies:** Task 5
**Description:**
- Implement conversation history truncation strategy
- Load last N messages (e.g., 50) from database
- Calculate approximate token count for context
- Implement sliding window if token limit approached
- Preserve system prompt and recent messages
- Add configuration for context window size

**Acceptance Criteria:**
- Long conversations don't exceed token limits
- Recent messages always included in context
- Context window size configurable
- Token counting approximation is reasonable

### Task 7: Agent System Prompt
**Priority:** P1 (Critical Path)
**Dependencies:** Task 3, Research
**Description:**
- Write comprehensive system prompt including:
  - Agent role and capabilities
  - Available tools and their purposes
  - Tool usage examples for common scenarios
  - Error handling instructions
  - User confirmation patterns
  - Response formatting guidelines
- Test prompt with various user inputs
- Iterate based on agent behavior

**Acceptance Criteria:**
- Agent correctly interprets task management commands
- Agent invokes appropriate tools for user requests
- Agent provides clear confirmations and error messages
- Agent handles ambiguous requests by asking clarifications

### Task 8: Tool Invocation Logging
**Priority:** P2 (Important)
**Dependencies:** Task 4, Task 5
**Description:**
- Capture tool invocations in message metadata
- Log tool name, parameters, execution time, result
- Store tool invocation data in Message.tool_calls field
- Implement structured logging for debugging
- Add metrics for tool success/failure rates

**Acceptance Criteria:**
- All tool invocations logged in database
- Tool metadata includes parameters and results
- Structured logs available for debugging
- Metrics tracked for monitoring

### Task 9: Error Handling and User Feedback
**Priority:** P2 (Important)
**Dependencies:** Task 5, Task 7
**Description:**
- Implement error handling for:
  - OpenAI API failures (rate limits, timeouts, errors)
  - MCP tool failures (validation errors, execution errors)
  - Database failures (connection errors, query errors)
- Generate user-friendly error messages
- Log errors with sufficient context for debugging
- Implement retry logic for transient failures

**Acceptance Criteria:**
- All error types handled gracefully
- User receives clear error messages
- Errors logged with stack traces and context
- Transient failures retried appropriately

### Task 10: Integration Testing
**Priority:** P2 (Important)
**Dependencies:** All above tasks
**Description:**
- Write integration tests for complete chat flow:
  - New conversation creation
  - Message persistence
  - Agent processing
  - Tool invocation
  - Response generation
- Test conversation continuity across requests
- Test user isolation (users can't access others' conversations)
- Test error scenarios (invalid inputs, API failures)
- Test conversation resume after simulated restart

**Acceptance Criteria:**
- All primary scenarios pass integration tests
- User isolation verified
- Conversation persistence verified
- Error handling verified
- Tests run in CI/CD pipeline

**Task Dependencies:**
```
Task 1 (DB Models) → Task 2 (Repository)
                   ↓
Research → Task 3 (Agent Init) → Task 4 (Tool Registration) → Task 5 (Chat Endpoint) → Task 6 (Context Mgmt)
                                                              ↓                        ↓
                                                         Task 7 (System Prompt)   Task 8 (Logging)
                                                              ↓                        ↓
                                                         Task 9 (Error Handling) → Task 10 (Integration Tests)
```

**Priority Order:**
1. P0: Tasks 1, 2, 3, 4 (Foundation)
2. P1: Tasks 5, 6, 7 (Core Functionality)
3. P2: Tasks 8, 9, 10 (Quality & Testing)

## Phase 3: Validation & Testing

**Validation Approach:**

### Unit Testing
- Test Conversation and Message models (validation, relationships)
- Test repository methods (CRUD operations, user isolation)
- Test agent initialization and configuration
- Test tool registration and invocation handlers
- Test context window management logic

### Integration Testing
- Test complete chat flow (request → agent → tools → response)
- Test conversation persistence and retrieval
- Test user authentication and authorization
- Test tool invocations with actual MCP server
- Test error handling for all failure modes

### End-to-End Testing
- Test primary user scenario (task management through chat)
- Test conversation continuity (multiple messages in sequence)
- Test conversation resume (after simulated restart)
- Test multi-turn refinement (agent asks clarifying questions)
- Test error scenarios (ambiguous commands, tool failures)

### Performance Testing
- Measure response time for typical requests (target: <5s)
- Test with concurrent users (target: 100 concurrent)
- Measure database query performance
- Test with long conversation histories

### Security Testing
- Verify JWT authentication enforcement
- Verify user isolation (cannot access others' conversations)
- Test input validation (SQL injection, XSS attempts)
- Verify tool invocations include correct user_id

**Success Criteria:**

1. **Functional Completeness** (from spec)
   - ✅ Users can create, view, update, complete, delete tasks via chat
   - ✅ Measured by: All task operations successful in integration tests

2. **Conversation Continuity** (from spec)
   - ✅ 100% of conversations persist across server restarts
   - ✅ Measured by: Restart test shows no data loss

3. **Response Quality** (from spec)
   - ✅ Agent correctly interprets intent in ≥90% of common requests
   - ✅ Measured by: Test suite with 50+ common commands

4. **User Isolation** (from spec)
   - ✅ Zero instances of cross-user data access
   - ✅ Measured by: Security tests with multiple users

5. **Performance** (from spec)
   - ✅ 95% of requests complete within 5 seconds
   - ✅ Measured by: Performance test with 100 requests

6. **Tool Invocation Accuracy** (from spec)
   - ✅ Agent invokes correct tools with proper parameters in ≥95% of cases
   - ✅ Measured by: Tool invocation logs analysis

7. **Demo Readiness** (from spec)
   - ✅ System demonstrates all primary scenarios without errors
   - ✅ Measured by: Successful demo run-through with judges

**Testing Strategy:**
- Unit tests run on every commit
- Integration tests run on pull requests
- E2E tests run before deployment
- Performance tests run weekly
- Security tests run before release

## Architectural Decision Records

### ADR Candidates

The following architectural decisions may warrant ADR documentation:

1. **Context Window Management Strategy**
   - Decision: Use sliding window with last N messages
   - Alternatives: Summarization, vector embeddings, full history
   - Impact: Affects conversation quality and token costs

2. **Agent System Prompt Design**
   - Decision: Comprehensive prompt with tool examples
   - Alternatives: Minimal prompt, few-shot learning, fine-tuned model
   - Impact: Affects agent accuracy and behavior consistency

3. **Tool Invocation Error Handling**
   - Decision: Graceful degradation with user-friendly messages
   - Alternatives: Strict failure, automatic retry, fallback responses
   - Impact: Affects user experience and system reliability

**Recommendation:** Document ADR #1 (Context Window Management) as it has long-term implications for scalability and cost.

## Next Steps

1. ✅ Complete Phase 0: Research (generate research.md)
2. ✅ Complete Phase 1: Design (generate data-model.md, contracts/, quickstart.md)
3. ⏭️ Execute Phase 2: Implementation (use /sp.tasks to generate tasks.md)
4. ⏭️ Execute Phase 3: Validation (run tests and verify success criteria)

**Ready for:** `/sp.tasks` to generate actionable task list from this plan
