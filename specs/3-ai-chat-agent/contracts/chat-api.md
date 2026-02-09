# Chat API Contract

**Version:** 1.0
**Date:** 2026-02-09
**Feature:** AI Chat Agent and Conversation System

## Overview

This document defines the HTTP API contract for the chat endpoint, including request/response schemas, error codes, and behavior specifications.

---

## Endpoint: Send Chat Message

### Request

**Method:** `POST`

**Path:** `/api/{user_id}/chat`

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| user_id | string | Yes | User identifier from JWT token |

**Headers:**

| Header | Type | Required | Description |
|--------|------|----------|-------------|
| Authorization | string | Yes | Bearer token (JWT) |
| Content-Type | string | Yes | Must be `application/json` |

**Request Body Schema:**

```json
{
  "message": "string (required, 1-10000 chars)",
  "conversation_id": "string (optional, UUID format)"
}
```

**Request Body Fields:**

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| message | string | Yes | 1-10000 characters | User's message to the agent |
| conversation_id | string | No | Valid UUID v4 | Existing conversation ID (omit for new conversation) |

**Example Request:**

```http
POST /api/user_123/chat HTTP/1.1
Host: api.example.com
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "message": "Add a task to buy groceries tomorrow",
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Example Request (New Conversation):**

```http
POST /api/user_123/chat HTTP/1.1
Host: api.example.com
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "message": "What tasks do I have today?"
}
```

---

### Response

**Success Response (200 OK):**

**Response Body Schema:**

```json
{
  "response": "string",
  "conversation_id": "string (UUID)",
  "message_id": "string (UUID)",
  "timestamp": "string (ISO 8601)",
  "tool_calls": [
    {
      "tool_name": "string",
      "status": "success | error"
    }
  ]
}
```

**Response Body Fields:**

| Field | Type | Description |
|-------|------|-------------|
| response | string | Agent's response message |
| conversation_id | string (UUID) | Conversation identifier (new or existing) |
| message_id | string (UUID) | Unique identifier for the agent's message |
| timestamp | string (ISO 8601) | When the response was generated |
| tool_calls | array (optional) | Summary of tools invoked (if any) |

**Example Success Response:**

```json
{
  "response": "I've added 'Buy groceries' to your tasks for tomorrow (February 10th). Is there anything else you'd like me to help with?",
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "message_id": "660e8400-e29b-41d4-a716-446655440001",
  "timestamp": "2026-02-09T20:30:00Z",
  "tool_calls": [
    {
      "tool_name": "add_task",
      "status": "success"
    }
  ]
}
```

---

### Error Responses

#### 400 Bad Request

**Cause:** Invalid request format or parameters

**Response Schema:**

```json
{
  "error": "string",
  "detail": "string",
  "field": "string (optional)"
}
```

**Example Scenarios:**

1. **Missing message field:**
```json
{
  "error": "Validation Error",
  "detail": "Field 'message' is required",
  "field": "message"
}
```

2. **Invalid conversation_id format:**
```json
{
  "error": "Validation Error",
  "detail": "conversation_id must be a valid UUID",
  "field": "conversation_id"
}
```

3. **Message too long:**
```json
{
  "error": "Validation Error",
  "detail": "Message exceeds maximum length of 10000 characters",
  "field": "message"
}
```

---

#### 401 Unauthorized

**Cause:** Missing or invalid JWT token

**Response Schema:**

```json
{
  "error": "Unauthorized",
  "detail": "string"
}
```

**Example Scenarios:**

1. **Missing Authorization header:**
```json
{
  "error": "Unauthorized",
  "detail": "Authorization header is required"
}
```

2. **Invalid JWT token:**
```json
{
  "error": "Unauthorized",
  "detail": "Invalid or expired token"
}
```

---

#### 403 Forbidden

**Cause:** User attempting to access another user's conversation

**Response Schema:**

```json
{
  "error": "Forbidden",
  "detail": "string"
}
```

**Example Scenario:**

```json
{
  "error": "Forbidden",
  "detail": "You do not have permission to access this conversation"
}
```

---

#### 404 Not Found

**Cause:** Conversation ID does not exist

**Response Schema:**

```json
{
  "error": "Not Found",
  "detail": "string"
}
```

**Example Scenario:**

```json
{
  "error": "Not Found",
  "detail": "Conversation not found"
}
```

---

#### 500 Internal Server Error

**Cause:** Server-side error (database, AI service, etc.)

**Response Schema:**

```json
{
  "error": "Internal Server Error",
  "detail": "string",
  "request_id": "string (optional)"
}
```

**Example Scenarios:**

1. **Database connection error:**
```json
{
  "error": "Internal Server Error",
  "detail": "Unable to process request. Please try again later.",
  "request_id": "req_abc123"
}
```

2. **OpenAI API error:**
```json
{
  "error": "Internal Server Error",
  "detail": "AI service temporarily unavailable. Please try again.",
  "request_id": "req_def456"
}
```

---

#### 504 Gateway Timeout

**Cause:** Agent processing exceeded timeout (30 seconds)

**Response Schema:**

```json
{
  "error": "Gateway Timeout",
  "detail": "string"
}
```

**Example Scenario:**

```json
{
  "error": "Gateway Timeout",
  "detail": "Request processing took too long. Please try again with a simpler message."
}
```

---

## Behavior Specifications

### Conversation Creation

- If `conversation_id` is omitted, a new conversation is created automatically
- New conversation ID is returned in the response
- Conversation title auto-generated from first user message (first 50 chars)

### Conversation Continuity

- If `conversation_id` is provided, conversation history is loaded
- Agent has access to previous messages for context
- Maximum 50 previous messages loaded (sliding window)

### User Isolation

- `user_id` in path must match `user_id` in JWT token
- Users cannot access conversations belonging to other users
- All database queries filtered by authenticated user_id

### Message Persistence

- User message persisted before agent processing
- Agent response persisted after successful generation
- Both messages include timestamps and metadata

### Tool Invocation

- Agent may invoke 0 or more tools per message
- Tool invocations logged in message metadata
- Tool results included in agent's response generation
- Tool failures communicated to user in natural language

### Error Handling

- Transient errors (network, timeout) may be retried by client
- Permanent errors (validation, authorization) should not be retried
- All errors include descriptive messages for debugging

---

## Rate Limiting

**Current Implementation:** No rate limiting (Phase III)

**Future Consideration:**
- 100 requests per minute per user
- 429 Too Many Requests response when exceeded

---

## Security Considerations

### Authentication

- All requests require valid JWT token
- Token must contain `user_id` claim
- Expired tokens rejected with 401

### Authorization

- Path parameter `user_id` must match JWT `user_id`
- Conversation access restricted to owner
- Tool invocations include authenticated user_id

### Input Validation

- Message content sanitized to prevent injection attacks
- conversation_id validated as UUID format
- Request body size limited to prevent DoS

### Data Protection

- All communication over HTTPS
- Conversation data encrypted at rest
- No sensitive data in error messages

---

## OpenAPI Specification

```yaml
openapi: 3.0.0
info:
  title: AI Chat Agent API
  version: 1.0.0
  description: Conversational AI agent for task management

paths:
  /api/{user_id}/chat:
    post:
      summary: Send a message to the AI agent
      operationId: sendChatMessage
      parameters:
        - name: user_id
          in: path
          required: true
          schema:
            type: string
          description: User identifier
      security:
        - bearerAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required:
                - message
              properties:
                message:
                  type: string
                  minLength: 1
                  maxLength: 10000
                  description: User's message to the agent
                conversation_id:
                  type: string
                  format: uuid
                  description: Existing conversation ID (optional)
      responses:
        '200':
          description: Successful response
          content:
            application/json:
              schema:
                type: object
                properties:
                  response:
                    type: string
                    description: Agent's response message
                  conversation_id:
                    type: string
                    format: uuid
                    description: Conversation identifier
                  message_id:
                    type: string
                    format: uuid
                    description: Message identifier
                  timestamp:
                    type: string
                    format: date-time
                    description: Response timestamp
                  tool_calls:
                    type: array
                    items:
                      type: object
                      properties:
                        tool_name:
                          type: string
                        status:
                          type: string
                          enum: [success, error]
        '400':
          description: Bad request
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'
        '401':
          description: Unauthorized
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'
        '403':
          description: Forbidden
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'
        '404':
          description: Not found
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'
        '500':
          description: Internal server error
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'
        '504':
          description: Gateway timeout
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'

components:
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
  schemas:
    Error:
      type: object
      properties:
        error:
          type: string
        detail:
          type: string
        field:
          type: string
        request_id:
          type: string
```

---

## Testing Checklist

- [ ] Valid request with new conversation returns 200
- [ ] Valid request with existing conversation returns 200
- [ ] Missing message field returns 400
- [ ] Invalid conversation_id format returns 400
- [ ] Message exceeding max length returns 400
- [ ] Missing Authorization header returns 401
- [ ] Invalid JWT token returns 401
- [ ] Mismatched user_id returns 403
- [ ] Non-existent conversation_id returns 404
- [ ] Database error returns 500
- [ ] OpenAI API error returns 500
- [ ] Request timeout returns 504
- [ ] Tool invocations logged correctly
- [ ] Conversation history loaded correctly
- [ ] User isolation enforced

---

**Contract Version:** 1.0
**Status:** Ready for implementation
