# API Contract: Todo Web Application Backend API

## Base URL
`/api/v1`

## Authentication
All endpoints require authentication via JWT token in the Authorization header:
```
Authorization: Bearer {jwt_token}
```
_Note: Authentication will be implemented in a future phase, but the API is designed to accommodate it._

## Common Response Format

### Success Responses
All successful responses return JSON with the following structure:
```json
{
  "id": integer,
  "title": "string",
  "description": "string",
  "status": "string",
  "user_id": integer,
  "created_at": "ISO 8601 datetime string",
  "updated_at": "ISO 8601 datetime string"
}
```

### Error Responses
All error responses follow this format:
```json
{
  "detail": "error message string"
}
```

## Endpoints

### Create Task
```
POST /api/v1/tasks
```

#### Description
Creates a new task for the authenticated user.

#### Request Headers
```
Content-Type: application/json
Authorization: Bearer {jwt_token}  // For future implementation
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
- `201 Created` - Task successfully created
- `400 Bad Request` - Invalid request body
- `401 Unauthorized` - Invalid or missing authentication (future)
- `422 Unprocessable Entity` - Validation error

#### Success Response (201)
```json
{
  "id": 1,
  "title": "Buy groceries",
  "description": "Milk, bread, eggs",
  "status": "pending",
  "user_id": 1,
  "created_at": "2026-01-21T12:30:00Z",
  "updated_at": "2026-01-21T12:30:00Z"
}
```

#### Error Response Examples
```json
{
  "detail": "Title is required and must be between 1 and 100 characters"
}
```

### Get All Tasks
```
GET /api/v1/tasks
```

#### Description
Retrieves all tasks for the authenticated user.

#### Request Headers
```
Authorization: Bearer {jwt_token}  // For future implementation
```

#### Response Codes
- `200 OK` - Successfully retrieved tasks
- `401 Unauthorized` - Invalid or missing authentication (future)

#### Success Response (200)
```json
[
  {
    "id": 1,
    "title": "Buy groceries",
    "description": "Milk, bread, eggs",
    "status": "pending",
    "user_id": 1,
    "created_at": "2026-01-21T12:30:00Z",
    "updated_at": "2026-01-21T12:30:00Z"
  },
  {
    "id": 2,
    "title": "Walk the dog",
    "description": "",
    "status": "completed",
    "user_id": 1,
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
Retrieves a specific task by its ID for the authenticated user.

#### Path Parameters
- `task_id` (integer): The ID of the task to retrieve

#### Request Headers
```
Authorization: Bearer {jwt_token}  // For future implementation
```

#### Response Codes
- `200 OK` - Task successfully retrieved
- `401 Unauthorized` - Invalid or missing authentication (future)
- `404 Not Found` - Task not found or doesn't belong to user

#### Success Response (200)
```json
{
  "id": 1,
  "title": "Buy groceries",
  "description": "Milk, bread, eggs",
  "status": "pending",
  "user_id": 1,
  "created_at": "2026-01-21T12:30:00Z",
  "updated_at": "2026-01-21T12:30:00Z"
}
```

#### Error Response (404)
```json
{
  "detail": "Task not found"
}
```

### Update Task
```
PUT /api/v1/tasks/{task_id}
```

#### Description
Updates an existing task with the specified ID.

#### Path Parameters
- `task_id` (integer): The ID of the task to update

#### Request Headers
```
Content-Type: application/json
Authorization: Bearer {jwt_token}  // For future implementation
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
- `200 OK` - Task successfully updated
- `400 Bad Request` - Invalid request body
- `401 Unauthorized` - Invalid or missing authentication (future)
- `404 Not Found` - Task not found or doesn't belong to user
- `422 Unprocessable Entity` - Validation error

#### Success Response (200)
```json
{
  "id": 1,
  "title": "Buy groceries - urgent",
  "description": "Milk, bread, eggs",
  "status": "completed",
  "user_id": 1,
  "created_at": "2026-01-21T12:30:00Z",
  "updated_at": "2026-01-21T13:45:00Z"
}
```

### Delete Task
```
DELETE /api/v1/tasks/{task_id}
```

#### Description
Deletes the specified task.

#### Path Parameters
- `task_id` (integer): The ID of the task to delete

#### Request Headers
```
Authorization: Bearer {jwt_token}  // For future implementation
```

#### Response Codes
- `204 No Content` - Task successfully deleted
- `401 Unauthorized` - Invalid or missing authentication (future)
- `404 Not Found` - Task not found or doesn't belong to user

#### Success Response (204)
No content returned (HTTP 204 No Content)

#### Error Response (404)
```json
{
  "detail": "Task not found"
}
```

## Validation Rules

### Task Title
- Required: Yes
- Min Length: 1 character
- Max Length: 100 characters

### Task Description
- Required: No (optional)
- Max Length: 1000 characters

### Task Status
- Required: No (defaults to "pending")
- Allowed Values: "pending", "completed"

## HTTP Status Codes

### Success Codes
- `200 OK` - Request successful
- `201 Created` - Resource created successfully
- `204 No Content` - Request successful, no content to return

### Client Error Codes
- `400 Bad Request` - Invalid request format
- `401 Unauthorized` - Authentication required (future)
- `404 Not Found` - Resource not found
- `422 Unprocessable Entity` - Validation error

### Server Error Codes
- `500 Internal Server Error` - Unexpected server error

## Error Message Guidelines

Error messages should be:
- Clear and descriptive
- User-friendly (avoid technical jargon when possible)
- Specific to the error condition
- Consistent with the error response format