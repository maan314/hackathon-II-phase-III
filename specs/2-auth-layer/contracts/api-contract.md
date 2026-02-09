# API Contract: Todo Web Application Authentication Layer

## Authentication Headers
All protected endpoints require authentication via JWT token in the Authorization header:
```
Authorization: Bearer {jwt_token}
```

## Authentication Error Responses
All authentication failures return a 401 status code with the following format:
```json
{
  "detail": "Could not validate credentials"
}
```

## Authorization Error Responses
All authorization failures (valid token but insufficient permissions) return a 403 status code:
```json
{
  "detail": "Access denied: insufficient permissions"
}
```

## Updated Task Endpoints with Authentication

### Create Task
```
POST /api/v1/tasks
```

#### Description
Creates a new task for the authenticated user.

#### Request Headers
```
Content-Type: application/json
Authorization: Bearer {valid_jwt_token}
```

#### Request Body
```json
{
  "title": "string (1-100 chars)",
  "description": "string (optional, 0-1000 chars)",
  "status": "string (optional, either 'pending' or 'completed', default: 'pending')"
}
```

#### Response Codes
- `201 Created` - Task successfully created and assigned to authenticated user
- `400 Bad Request` - Invalid request body
- `401 Unauthorized` - Invalid or missing authentication token
- `422 Unprocessable Entity` - Validation error

#### Success Response (201)
```json
{
  "id": 1,
  "title": "Buy groceries",
  "description": "Milk, bread, eggs",
  "status": "pending",
  "user_id": 12345,  // Matches authenticated user_id from token
  "created_at": "2026-01-21T12:30:00Z",
  "updated_at": "2026-01-21T12:30:00Z"
}
```

### Get All Tasks
```
GET /api/v1/tasks
```

#### Description
Retrieves all tasks for the authenticated user only.

#### Request Headers
```
Authorization: Bearer {valid_jwt_token}
```

#### Response Codes
- `200 OK` - Successfully retrieved tasks for authenticated user
- `401 Unauthorized` - Invalid or missing authentication token

#### Success Response (200)
```json
[
  {
    "id": 1,
    "title": "Buy groceries",
    "description": "Milk, bread, eggs",
    "status": "pending",
    "user_id": 12345,  // Always matches authenticated user_id
    "created_at": "2026-01-21T12:30:00Z",
    "updated_at": "2026-01-21T12:30:00Z"
  },
  {
    "id": 2,
    "title": "Walk the dog",
    "description": "",
    "status": "completed",
    "user_id": 12345,  // Always matches authenticated user_id
    "created_at": "2026-01-21T11:15:00Z",
    "updated_at": "2026-01-21T11:20:00Z"
  }
]
```

### Get Specific Task
```
GET /api/v1/tasks/{task_id}
```

#### Description
Retrieves a specific task by its ID, but only if it belongs to the authenticated user.

#### Path Parameters
- `task_id` (integer): The ID of the task to retrieve

#### Request Headers
```
Authorization: Bearer {valid_jwt_token}
```

#### Response Codes
- `200 OK` - Task successfully retrieved (belongs to authenticated user)
- `401 Unauthorized` - Invalid or missing authentication token
- `403 Forbidden` - Task exists but belongs to another user
- `404 Not Found` - Task does not exist

#### Success Response (200)
```json
{
  "id": 1,
  "title": "Buy groceries",
  "description": "Milk, bread, eggs",
  "status": "pending",
  "user_id": 12345,  // Matches authenticated user_id from token
  "created_at": "2026-01-21T12:30:00Z",
  "updated_at": "2026-01-21T12:30:00Z"
}
```

#### Error Response (403)
```json
{
  "detail": "Access denied: insufficient permissions"
}
```

### Update Task
```
PUT /api/v1/tasks/{task_id}
```

#### Description
Updates an existing task with the specified ID, but only if it belongs to the authenticated user.

#### Path Parameters
- `task_id` (integer): The ID of the task to update

#### Request Headers
```
Content-Type: application/json
Authorization: Bearer {valid_jwt_token}
```

#### Request Body
```json
{
  "title": "string (1-100 chars)",
  "description": "string (optional, 0-1000 chars)",
  "status": "string (either 'pending' or 'completed')"
}
```

#### Response Codes
- `200 OK` - Task successfully updated (belongs to authenticated user)
- `400 Bad Request` - Invalid request body
- `401 Unauthorized` - Invalid or missing authentication token
- `403 Forbidden` - Task exists but belongs to another user
- `404 Not Found` - Task does not exist
- `422 Unprocessable Entity` - Validation error

#### Success Response (200)
```json
{
  "id": 1,
  "title": "Buy groceries - urgent",
  "description": "Milk, bread, eggs",
  "status": "completed",
  "user_id": 12345,  // Matches authenticated user_id from token
  "created_at": "2026-01-21T12:30:00Z",
  "updated_at": "2026-01-21T13:45:00Z"
}
```

### Delete Task
```
DELETE /api/v1/tasks/{task_id}
```

#### Description
Deletes the specified task, but only if it belongs to the authenticated user.

#### Path Parameters
- `task_id` (integer): The ID of the task to delete

#### Request Headers
```
Authorization: Bearer {valid_jwt_token}
```

#### Response Codes
- `204 No Content` - Task successfully deleted (belonged to authenticated user)
- `401 Unauthorized` - Invalid or missing authentication token
- `403 Forbidden` - Task exists but belongs to another user
- `404 Not Found` - Task does not exist

#### Success Response (204)
No content returned (HTTP 204 No Content)

## Token Validation Rules

### JWT Format
- Must be in proper JWT format: `header.payload.signature` (3 parts separated by dots)
- Header must contain valid algorithm (HS256 recommended)
- Payload must contain required claims: `sub`, `exp`, `iat`

### JWT Claims
- `sub` (subject): Must contain valid user_id as integer
- `exp` (expiration): Must be a future timestamp
- `iat` (issued at): Must be a past or current timestamp
- `jti` (JWT ID): Optional but recommended for security

### Token Validation Process
1. Verify JWT signature using shared secret
2. Check token expiration against current time
3. Validate token was not issued in the future
4. Extract user_id from `sub` claim
5. Verify user_id corresponds to an active user in the system

## Security Requirements

### Transport Security
- All JWT tokens must be transmitted over HTTPS
- Authorization headers must not be logged or stored insecurely

### Token Storage (Client Side)
- Tokens should be stored securely (httpOnly cookies recommended)
- Tokens should be cleared on logout
- Tokens should be refreshed periodically if long-lived access is needed

### Rate Limiting
- Authentication attempts should be rate-limited to prevent brute-force attacks
- Failed authentication attempts should be logged for security monitoring