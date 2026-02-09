# API Contract: Todo Web Application Frontend UI

## Authentication Endpoints

### Sign Up
```
POST /api/auth/signup
```

#### Description
Registers a new user with the provided information.

#### Request Headers
```
Content-Type: application/json
```

#### Request Body
```json
{
  "email": "user@example.com",
  "password": "securePassword123!",
  "firstName": "John",
  "lastName": "Doe",
  "agreeTerms": true
}
```

#### Response Codes
- `201 Created` - User successfully registered
- `400 Bad Request` - Validation error
- `409 Conflict` - User already exists

#### Success Response (201)
```json
{
  "message": "User registered successfully"
}
```

#### Error Response Examples
```json
{
  "error": "Email is required"
}
```
```json
{
  "error": "Email format is invalid"
}
```
```json
{
  "error": "User already exists"
}
```

### Sign In
```
POST /api/auth/signin
```

#### Description
Authenticates an existing user and returns an access token.

#### Request Headers
```
Content-Type: application/json
```

#### Request Body
```json
{
  "email": "user@example.com",
  "password": "securePassword123!"
}
```

#### Response Codes
- `200 OK` - User successfully authenticated
- `401 Unauthorized` - Invalid credentials

#### Success Response (200)
```json
{
  "accessToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refreshToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 12345,
    "email": "user@example.com",
    "firstName": "John",
    "lastName": "Doe"
  }
}
```

#### Error Response (401)
```json
{
  "error": "Invalid credentials"
}
```

### Protected Dashboard Access
```
GET /api/dashboard
```

#### Description
Accesses the user dashboard with authentication required.

#### Request Headers
```
Authorization: Bearer {accessToken}
```

#### Response Codes
- `200 OK` - Successfully accessed dashboard data
- `401 Unauthorized` - Invalid or expired token

#### Success Response (200)
```json
{
  "data": {
    "tasks": [],
    "stats": {}
  }
}
```

#### Error Response (401)
```json
{
  "error": "Unauthorized access"
}
```

## Common Response Format

### Success Responses
All successful responses return JSON with the following possible structure:
```json
{
  "message": "descriptive message",
  "data": {}  // optional, depends on the endpoint
}
```

### Error Responses
All error responses follow this format:
```json
{
  "error": "descriptive error message"
}
```

### Error Response with Code
Some errors may include an error code for client-side handling:
```json
{
  "error": "descriptive error message",
  "errorCode": "UNAUTHORIZED_ACCESS"
}
```

## Validation Rules

### Sign Up Validation
- **Email:** Required, valid email format, max 255 characters
- **Password:** Required, 8-128 characters with strength requirements
- **FirstName:** Required, 1-50 characters
- **LastName:** Required, 1-50 characters
- **AgreeTerms:** Required, must be true

### Sign In Validation
- **Email:** Required, valid email format
- **Password:** Required, 8+ characters

## HTTP Status Codes

### Success Codes
- `200 OK` - Request successful
- `201 Created` - Resource created successfully

### Client Error Codes
- `400 Bad Request` - Validation error
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `409 Conflict` - Resource conflict (e.g., duplicate user)

### Server Error Codes
- `500 Internal Server Error` - Unexpected server error

## Authentication Headers

### Token Authorization
All protected endpoints require the following header:
```
Authorization: Bearer {jwt_token}
```

## Error Message Guidelines

Error messages should be:
- Clear and descriptive
- User-friendly (avoid technical jargon when possible)
- Specific to the error condition
- Consistent with the error response format
- Never expose sensitive system information

## Form Validation Messages

### Email Validation
- "Email is required"
- "Email format is invalid"
- "Email is too long (max 255 characters)"

### Password Validation
- "Password is required"
- "Password must be at least 8 characters"
- "Password must be less than 128 characters"
- "Password must include uppercase, lowercase, number, and special character"

### Name Validation
- "First name is required"
- "Last name is required"
- "Name is too long (max 50 characters)"

### Terms Agreement
- "You must agree to the terms of service"