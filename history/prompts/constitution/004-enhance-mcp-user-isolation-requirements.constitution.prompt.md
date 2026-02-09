---
id: 004
title: Enhance MCP User Isolation Requirements
stage: constitution
date: 2026-02-09
surface: agent
model: claude-opus-4-6
feature: none
branch: 3-mcp-task-tools
user: HP
command: /sp.constitution
labels: ["constitution", "mcp", "security", "user-isolation", "jwt"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
  - .specify/templates/plan-template.md
  - .specify/templates/spec-template.md
tests: []
---

# Prompt

```text
/sp.constitution

Project: MCP-based Task Management Tool Server for AI Todo Agent

Core principles:
- Stateless tool execution with database persistence
- Strict schema validation for tool inputs/outputs
- User-level data isolation enforced at tool layer
- Deterministic and reproducible tool behavior

Key standards:
- All tools operate via SQLModel + Neon PostgreSQL
- user_id required for every tool call
- JSON schemas must match hackathon specification
- Tools must not contain AI logic

Constraints:
- MCP Server: Official MCP SDK
- Backend: FastAPI Python
- Database: Neon PostgreSQL
- Authentication: JWT user identity propagation

Success criteria:
- Agent successfully calls MCP tools
- Tools persist tasks in Neon DB
- Tool responses match required JSON examples
- Errors handled gracefully and returned to agent
```

# Response

## Constitution Updated: v2.2.0 → v2.3.0

### Version Bump Rationale
**MINOR version increment** - Added two new standards (10, 11) and one new constraint (7) that materially expand governance requirements around user identity and data isolation.

### Changes Made

#### Enhanced Principles
1. **Principle 6: Tools as Exclusive Interface for Task Mutation**
   - Added requirement: Every tool call MUST include user_id
   - Enhanced rationale to include user-level data isolation at tool boundary

2. **Principle 7: Stateless MCP Server with Database Persistence and User Isolation**
   - Added requirement: Every tool MUST enforce user_id filtering to prevent cross-user data access
   - Enhanced rationale to guarantee users can only access their own data through strict tool-layer enforcement

#### New Standards Added
3. **Standard 10: User ID Propagation for All Tool Calls**
   - Rule: Every MCP tool invocation MUST include user_id as required parameter
   - Requirement: user_id extracted from JWT token and propagated to all tool calls
   - Rationale: Ensures all tool operations performed in authenticated user context

4. **Standard 11: Tool-Layer User Isolation**
   - Rule: MCP tools MUST enforce user-level data isolation at database query level
   - Requirement: All database queries within tools MUST filter by user_id
   - Rationale: Defense-in-depth security preventing cross-user data leakage

#### New Constraint Added
5. **Constraint 7: JWT User Identity Propagation**
   - Rule: User identity MUST be propagated from JWT tokens to all MCP tool invocations
   - Requirement: Backend extracts user_id from validated JWT tokens; tools reject user_id from untrusted sources
   - Rationale: Ensures cryptographically verified user identity, prevents impersonation

#### Testing Requirements Enhanced
- Added: User isolation testing to verify tools reject cross-user data access
- Added: JWT user identity propagation testing
- Added: Tool parameter validation testing for user_id requirement

#### Security Considerations Enhanced
- Added: User identity extraction from validated JWT tokens only
- Added: Tool-layer user isolation enforcement through database query filtering
- Added: Tool invocation validation for user_id presence and authentication match

### Template Propagation

#### Updated Templates
1. **`.specify/templates/plan-template.md`**
   - Added Standards 10 & 11 to Key Standards Compliance section
   - Added Constraint 7 to Constraints Verification section

2. **`.specify/templates/spec-template.md`**
   - Added JWT user identity propagation to Constitutional Constraints
   - Added user_id requirement to Constitutional Constraints
   - Added three new security requirements to Security Considerations

### Files Modified
- `.specify/memory/constitution.md` (version 2.3.0)
- `.specify/templates/plan-template.md`
- `.specify/templates/spec-template.md`

### Validation Status
- ✅ No unresolved placeholders
- ✅ Version line matches report (2.3.0)
- ✅ Dates in ISO format (2026-02-09)
- ✅ All principles declarative and testable
- ✅ Templates synchronized with new requirements

### Suggested Commit Message
```
docs: amend constitution to v2.3.0 (add MCP user isolation standards)

- Add Standard 10: User ID Propagation for All Tool Calls
- Add Standard 11: Tool-Layer User Isolation
- Add Constraint 7: JWT User Identity Propagation
- Enhance Principles 6 & 7 with user_id requirements
- Update plan and spec templates with new standards
- Add user isolation and JWT testing requirements
```

## Outcome

Constitution successfully updated with enhanced MCP security requirements focusing on:
- Mandatory user_id propagation from JWT tokens to all tool calls
- Tool-layer enforcement of user data isolation at database query level
- Defense-in-depth security preventing cross-user data access
- Clear separation between trusted (JWT) and untrusted (request params) user identity sources

All dependent templates synchronized to reflect new governance requirements.
