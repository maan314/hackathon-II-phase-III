<!-- SYNC IMPACT REPORT
Version change: 2.2.0 → 2.3.0
Modified principles:
  - Principle 6: Enhanced with explicit user_id requirement for all tool calls
  - Principle 7: Enhanced with user-level data isolation enforcement at tool layer
Added sections:
  - Standard 10: User ID Propagation for All Tool Calls
  - Standard 11: Tool-Layer User Isolation
  - Constraint 7: JWT User Identity Propagation
Removed sections: None
Templates requiring updates:
  ✅ .specify/templates/plan-template.md (Constitution Check includes user isolation requirements)
  ✅ .specify/templates/spec-template.md (Security Considerations include user_id enforcement)
  ⚠ .specify/templates/tasks-template.md (not found - may need creation)
Follow-up TODOs: None - all available templates updated.
Rationale for MINOR version bump: Added two new standards (10, 11) and one new constraint (7) that materially expand governance requirements around user identity and data isolation.
-->
# Project Constitution

**Version:** 2.3.0
**Ratification Date:** 2026-01-21
**Last Amended:** 2026-02-09

## Purpose

This constitution establishes the foundational principles and governance framework for the AI Chat Agent and Conversation System with MCP Server and Tooling Integration for Todo App (Phase III) project. It serves as the authoritative guide for all development decisions, ensuring consistency, quality, and alignment across all project activities.

## Core Principles

### Principle 1: Stateless Server Architecture with Persistent Conversation Storage
- **Rule:** The AI chat server MUST be stateless.
- **Requirement:** All conversation state MUST be persisted in Neon PostgreSQL and retrieved per request. No in-memory session state is allowed.
- **Rationale:** Ensures scalability, resilience, and enables conversations to resume after server restarts, providing seamless user experience.

### Principle 2: Tool-Driven AI Behavior
- **Rule:** AI agent actions MUST be exclusively constrained to approved MCP tools.
- **Requirement:** No direct database writes or external system modifications are permitted outside tool boundaries. Data modification MUST occur only through MCP tool invocations.
- **Rationale:** Maintains system integrity, prevents unauthorized operations, and enforces business logic through controlled interfaces.

### Principle 3: Deterministic Agent Execution via OpenAI Agents SDK
- **Rule:** AI agents MUST execute deterministically.
- **Requirement:** Agent behavior MUST be consistent, predictable, and reproducible across identical inputs and conversation states using the OpenAI Agents SDK.
- **Rationale:** Ensures reliable AI behavior, predictable user experiences, and simplifies debugging and auditing.

### Principle 4: Traceable Conversation Logs for Auditability
- **Rule:** All AI agent interactions MUST be logged for auditability and debugging purposes.
- **Requirement:** Structured logging for tool_calls, responses, and conversation flow MUST be implemented.
- **Rationale:** Enables system monitoring, performance analysis, debugging, and compliance verification.

### Principle 5: Natural Language to Structured Tool Invocation
- **Rule:** The AI agent MUST correctly interpret natural language commands and convert them into structured tool invocations.
- **Requirement:** All task operations MUST be executed via MCP tools following OpenAI Agents SDK patterns, and the agent MUST confirm actions in natural language before execution.
- **Rationale:** Provides intuitive and safe user interaction, ensuring precise operations on user data through controlled, well-defined interfaces.

### Principle 6: Tools as Exclusive Interface for Task Mutation
- **Rule:** MCP tools are the ONLY permitted interface for task data mutation, and every tool call MUST include user_id.
- **Requirement:** All task creation, modification, completion, and deletion operations MUST be performed exclusively through MCP tools with user_id as a required parameter. No direct database access or alternative mutation paths are allowed.
- **Rationale:** Enforces a single source of truth for task operations, ensures consistent validation and business logic application, maintains clear audit trails for all task changes, and enables user-level data isolation at the tool boundary.

### Principle 7: Stateless MCP Server with Database Persistence and User Isolation
- **Rule:** The MCP server MUST be stateless with all state persisted in the database, and user-level data isolation MUST be enforced at the tool layer.
- **Requirement:** MCP tools MUST NOT maintain in-memory state between invocations. All task data MUST be persisted in Neon PostgreSQL and retrieved per tool invocation. Every tool MUST enforce user_id filtering to prevent cross-user data access.
- **Rationale:** Enables horizontal scaling of MCP servers, ensures data durability, allows tools to be invoked from multiple agent instances without state conflicts, and guarantees that users can only access their own data through strict tool-layer enforcement.

### Principle 8: Tool Schema Strict Validation
- **Rule:** All MCP tools MUST enforce strict schema validation on inputs and outputs.
- **Requirement:** Tool parameters MUST be validated against defined JSON schemas before execution. Tool responses MUST conform to documented output schemas.
- **Rationale:** Prevents invalid data from entering the system, ensures predictable tool behavior, and enables reliable agent-tool integration.

### Principle 9: Agent-Tool Separation of Concerns
- **Rule:** Clear separation MUST be maintained between AI agent logic and tool implementation.
- **Requirement:** Tools MUST contain only pure CRUD operations with no AI logic, natural language processing, or decision-making. Agent MUST handle all natural language interpretation and tool selection.
- **Rationale:** Maintains modularity, enables independent testing and evolution of agent and tools, and prevents logic duplication across system boundaries.

## Key Standards

### Standard 1: Chat State Persistence
- **Rule:** All chat state MUST be persisted in Neon PostgreSQL.
- **Rationale:** Ensures data durability, consistency, and enables conversation continuity across sessions and server restarts.

### Standard 2: Agent Interaction via MCP Tools
- **Rule:** The agent MUST use MCP tools only to modify tasks.
- **Rationale:** Enforces controlled data manipulation and adheres to the tool-driven AI behavior principle.

### Standard 3: Conversation History Retrieval
- **Rule:** Conversation history MUST be retrieved per request.
- **Rationale:** Supports stateless server architecture and ensures that the agent always operates on the most current conversation context.

### Standard 4: No In-Memory Session State
- **Rule:** No in-memory session state is allowed.
- **Rationale:** Essential for horizontal scalability, fault tolerance, and consistent behavior across distributed environments.

### Standard 5: Structured Logging
- **Rule:** Structured logging for tool_calls and responses MUST be implemented.
- **Rationale:** Facilitates efficient debugging, monitoring, and auditing of agent interactions and system behavior.

### Standard 6: MCP Tool Schema Compliance
- **Rule:** MCP tools MUST match provided JSON schemas exactly.
- **Requirement:** Tool input parameters and output structures MUST conform to documented schemas without deviation.
- **Rationale:** Ensures predictable tool behavior, enables automatic validation, and maintains compatibility with agent expectations.

### Standard 7: Tool State Persistence
- **Rule:** Tools MUST persist all state changes in Neon PostgreSQL.
- **Requirement:** Every tool invocation that modifies task data MUST result in a database write. No state may be cached or held in memory between invocations.
- **Rationale:** Guarantees data durability, enables stateless tool execution, and ensures consistency across distributed tool instances.

### Standard 8: Pure CRUD Tools (No AI Logic)
- **Rule:** MCP tools MUST contain only pure CRUD operations with no AI logic.
- **Requirement:** Tools MUST NOT perform natural language processing, intent recognition, or decision-making. All logic MUST be deterministic data operations.
- **Rationale:** Maintains clear separation of concerns, simplifies tool testing, and prevents logic duplication between agent and tools.

### Standard 9: Structured Tool Responses
- **Rule:** Every tool invocation MUST return a structured response.
- **Requirement:** Tool responses MUST include status (success/failure), result data (if successful), and error details (if failed) in a consistent format.
- **Rationale:** Enables reliable error handling, facilitates agent response generation, and provides clear feedback for debugging.

### Standard 10: User ID Propagation for All Tool Calls
- **Rule:** Every MCP tool invocation MUST include user_id as a required parameter.
- **Requirement:** The user_id MUST be extracted from the JWT token and propagated to all tool calls. Tools MUST reject invocations that lack a valid user_id.
- **Rationale:** Ensures that all tool operations are performed in the context of an authenticated user, enabling proper data isolation, audit trails, and authorization enforcement.

### Standard 11: Tool-Layer User Isolation
- **Rule:** MCP tools MUST enforce user-level data isolation at the database query level.
- **Requirement:** All database queries within tools MUST filter by user_id. Tools MUST NOT return or modify data belonging to other users under any circumstances.
- **Rationale:** Provides defense-in-depth security by enforcing isolation at the tool layer, preventing cross-user data leakage even if higher-level authorization checks fail.

## Constraints

### Constraint 1: Backend Framework
- **Rule:** The backend MUST be implemented using FastAPI + OpenAI Agents SDK.
- **Rationale:** Provides a robust, high-performance, and type-safe framework for API development and agent integration.

### Constraint 2: ORM and Database
- **Rule:** The ORM MUST be SQLModel and the database MUST be Neon PostgreSQL.
- **Rationale:** Ensures consistent, type-safe, and scalable data access and storage for conversation data.

### Constraint 3: Authentication
- **Rule:** Authentication MUST use Better Auth with user_id enforcement.
- **Rationale:** Guarantees secure user identification and authorization across the system.

### Constraint 4: API Endpoint
- **Rule:** The primary chat endpoint MUST be POST /api/{user_id}/chat and operate in a stateless manner.
- **Rationale:** Defines the core interaction point for the AI agent, adhering to stateless principles.

### Constraint 5: MCP SDK Usage
- **Rule:** MCP server and tools MUST be implemented using the Official MCP SDK.
- **Requirement:** FastAPI integration with MCP server MUST follow MCP SDK patterns and conventions.
- **Rationale:** Ensures compatibility with MCP ecosystem, leverages tested implementations, and maintains standard tool interfaces.

### Constraint 6: MCP Tool Set
- **Rule:** The following MCP tools MUST be implemented: add_task, list_tasks, complete_task, delete_task, update_task.
- **Requirement:** Each tool MUST follow MCP SDK conventions for registration, parameter validation, and response formatting.
- **Rationale:** Defines the minimum viable tool set for task management functionality and ensures consistent tool naming.

### Constraint 7: JWT User Identity Propagation
- **Rule:** User identity MUST be propagated from JWT tokens to all MCP tool invocations.
- **Requirement:** The backend MUST extract user_id from validated JWT tokens and pass it as a required parameter to every tool call. Tools MUST NOT accept user_id from untrusted sources (e.g., request body or query parameters).
- **Rationale:** Ensures that user identity is cryptographically verified before tool execution, preventing user impersonation and unauthorized data access.

## Success Criteria

### Criterion 1: Natural Language Interpretation
- **Metric:** The AI agent correctly interprets natural language commands.
- **Validation:** Agent responses demonstrate accurate understanding and appropriate tool invocation.

### Criterion 2: Conversation Resume Capability
- **Metric:** Conversations resume successfully after a server restart.
- **Validation:** User conversation history is correctly loaded and processed post-restart.

### Criterion 3: Task Operations via MCP Tools
- **Metric:** Task operations are executed only via MCP tools.
- **Validation:** All modifications to tasks are initiated by validated MCP tool invocations, not direct agent actions.

### Criterion 4: Agent Action Confirmation
- **Metric:** The agent confirms actions in natural language.
- **Validation:** Before executing a command, the agent clearly communicates its intended action to the user.

### Criterion 5: MCP Tool Invocation Success
- **Metric:** Agent successfully invokes MCP tools for all task operations.
- **Validation:** Tool invocation logs show successful parameter passing, execution, and response handling for all 5 tool types.

### Criterion 6: Tool Database Persistence
- **Metric:** Tools modify tasks in Neon DB correctly.
- **Validation:** Database inspection confirms all tool-initiated changes are persisted with correct data and timestamps.

### Criterion 7: Tool Response Structure
- **Metric:** Tool responses are returned to AI agent in structured format.
- **Validation:** All tool responses include status, result/error, and conform to documented schemas.

### Criterion 8: Stateless Tool Execution
- **Metric:** Stateless tool execution is verified.
- **Validation:** Tools can be invoked from multiple agent instances without state conflicts or data inconsistencies.

## Governance

### Amendment Procedure
- Changes to this constitution MUST be proposed in writing with clear justification.
- Amendments require consensus among project stakeholders before implementation.
- Updated constitution MUST be ratified with new version and amendment date.

### Versioning Policy
- MAJOR version increments for backward-incompatible governance/principle changes.
- MINOR version increments for new principles or expanded guidance.
- PATCH version increments for clarifications and non-semantic refinements.

### Compliance Review
- Regular constitution compliance reviews MUST be conducted during milestone assessments.
- All project decisions SHOULD reference applicable constitutional principles.
- Deviations from constitutional principles MUST be documented and justified.

## Quality Assurance

### Testing Requirements
- All code changes MUST include appropriate unit, integration, and end-to-end tests.
- Test coverage MUST meet predetermined thresholds before code acceptance.
- Database operations MUST be tested for transaction integrity and error handling.
- AI agent behavior MUST be tested for natural language interpretation and tool invocation.
- Authentication and authorization flows MUST be comprehensively tested.
- Conversation persistence and retrieval MUST be tested for data integrity.
- MCP tools MUST be tested independently for correct CRUD operations and schema compliance.
- Agent-tool integration MUST be tested for successful invocation and response handling.
- User isolation MUST be tested to verify that tools reject cross-user data access attempts.
- JWT user identity propagation MUST be tested to ensure user_id is correctly extracted and passed to tools.
- Tool parameter validation MUST be tested to verify that tools reject invocations without valid user_id.

### Code Quality Standards
- All code MUST pass static analysis and linting checks.
- Pull requests MUST undergo peer review before merging.
- Critical paths MUST include comprehensive error handling and logging.

## Risk Management

### Data Integrity Protection
- Database operations MUST include proper validation and sanitization.
- Backup and recovery procedures MUST be defined and tested.
- Data migration strategies MUST ensure zero-downtime transitions.

### Security Considerations
- All external inputs MUST be validated and sanitized.
- Authentication flows MUST be tested for security vulnerabilities.
- Security audits MUST be conducted regularly as the system evolves.
- AI agent access controls MUST be implemented securely.
- MCP tool permissions MUST be properly configured to prevent unauthorized operations.
- Conversation data MUST be encrypted at rest and in transit.
- Tool input validation MUST prevent injection attacks and malformed data.
- User identity MUST be extracted from validated JWT tokens only, never from untrusted request parameters.
- Tool-layer user isolation MUST be enforced through database query filtering to prevent cross-user data access.
- All tool invocations MUST validate that user_id is present and matches the authenticated user's identity.
