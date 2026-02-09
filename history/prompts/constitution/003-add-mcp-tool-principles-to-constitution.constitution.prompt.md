---
id: "003"
title: "Add MCP Tool Principles to Constitution"
stage: "constitution"
date_iso: "2026-02-09"
surface: "agent"
model: "claude-opus-4-6"
feature: "none"
branch: "2-ai-chat-agent"
user: "user"
command: "/sp.constitution"
labels: ["constitution", "mcp-tools", "governance", "principles"]
link_spec: null
link_ticket: null
link_adr: null
link_pr: null
files_yaml: |
 - ".specify/memory/constitution.md"
 - ".specify/templates/plan-template.md"
 - ".specify/templates/spec-template.md"
tests_yaml: |
 - "none"
outcome: "Successfully updated constitution to v2.2.0 with MCP Server and Tooling Integration principles"
evaluation: "Constitution now includes 4 new principles, 4 new standards, 2 new constraints, and 4 new success criteria for MCP tool integration. All templates synchronized."
---

# Prompt History Record

## Original Prompt
```
Project: MCP Server and Tooling Integration for AI Todo Management

Core principles:
- Tools as the ONLY interface for task mutation
- Stateless MCP server with database persistence
- Tool schema strict validation
- Agent-tool separation of concerns

Key standards:
- MCP tools must match provided JSON schemas
- Tools must persist state in Neon PostgreSQL
- No AI logic inside tools (pure CRUD)
- Structured responses for every tool invocation

Constraints:
- Use Official MCP SDK
- FastAPI integration with MCP server
- SQLModel ORM
- Tools: add_task, list_tasks, complete_task, delete_task, update_task

Success criteria:
- Agent successfully invokes MCP tools
- Tools modify tasks in Neon DB
- Tool responses returned to AI agent
- Stateless tool execution verified
```

## Response Summary
Updated the project constitution to version 2.2.0 (MINOR version bump) by adding comprehensive MCP Server and Tooling Integration principles while preserving all existing AI Chat Agent principles.

**New Principles Added (4):**
- Principle 6: Tools as Exclusive Interface for Task Mutation
- Principle 7: Stateless MCP Server with Database Persistence
- Principle 8: Tool Schema Strict Validation
- Principle 9: Agent-Tool Separation of Concerns

**New Standards Added (4):**
- Standard 6: MCP Tool Schema Compliance
- Standard 7: Tool State Persistence
- Standard 8: Pure CRUD Tools (No AI Logic)
- Standard 9: Structured Tool Responses

**New Constraints Added (2):**
- Constraint 5: MCP SDK Usage (Official MCP SDK required)
- Constraint 6: MCP Tool Set (add_task, list_tasks, complete_task, delete_task, update_task)

**New Success Criteria Added (4):**
- Criterion 5: MCP Tool Invocation Success
- Criterion 6: Tool Database Persistence
- Criterion 7: Tool Response Structure
- Criterion 8: Stateless Tool Execution

**Templates Synchronized:**
- `.specify/templates/plan-template.md`: Updated Constitution Check section with all 9 principles and 9 standards
- `.specify/templates/spec-template.md`: Updated Constraints section with MCP SDK and tool requirements, added tool validation to Security Considerations

**Version Bump Rationale:**
MINOR version (2.1.0 → 2.2.0) because new principles and standards were added without removing or redefining existing ones. This is backward-compatible expansion of governance framework.

**Constitution Now Covers:**
- 9 Core Principles (5 existing + 4 new MCP tool principles)
- 9 Key Standards (5 existing + 4 new MCP tool standards)
- 6 Constraints (4 existing + 2 new MCP constraints)
- 8 Success Criteria (4 existing + 4 new MCP criteria)

## Files Modified
- `.specify/memory/constitution.md`: Updated to v2.2.0 with MCP tool principles
- `.specify/templates/plan-template.md`: Added MCP principles to Constitution Check
- `.specify/templates/spec-template.md`: Added MCP constraints and security requirements
