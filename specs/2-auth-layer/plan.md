# Todo Web Application Authentication Layer Implementation Plan

## Feature Context

**Feature:** Todo Web Application Authentication Layer
**Branch:** 2-auth-layer
**Spec:** specs/2-auth-layer/spec.md

## Technical Context

**Architecture:** Middleware-based JWT authentication layer integrated with existing FastAPI backend
**Technologies:**
- FastAPI framework for middleware implementation
- python-jose for JWT token handling
- passlib for password hashing (if needed for user validation)
- Environment variables for shared secret configuration
**Infrastructure:**
- Shared secret for JWT signing/verification stored in environment variables
- HTTP Bearer token authorization scheme
- Stateless authentication with no server-side session storage
**Security:**
- JWT token validation with signature and expiration checking
- User identity extraction from validated tokens
- Enforced user isolation for task access

## Constitution Check

**Principles Applied:**
- **Zero Trust Between Frontend and Backend:** All identity verification occurs server-side, not trusting frontend data
- **Stateless Authentication:** Using JWT tokens with no server-side session storage
- **Explicit Authorization Checks:** Every protected endpoint performs authorization checks
- **User Data Isolation:** All data queries filtered by authenticated user identity
- **Server-Side Identity Verification:** JWT tokens validated server-side with shared secret
- **Security-First Architecture:** Authentication implemented as a core system component
- **Clear Separation of Backend Responsibilities:** Authentication logic separated from business logic

**Compliance Status:**
- ✅ All constitutional principles satisfied
- ✅ Identity verification occurs server-side with proper JWT validation
- ✅ User isolation enforced through token-based authorization
- ✅ Stateless authentication implemented with JWT tokens
- ✅ Implementation adheres to approved specification

## Gates

### Gate 1: Requirements Clarity
- [x] All functional requirements are understood
- [x] All non-functional requirements are understood
- [x] All constraints are understood
- [x] All success criteria are understood

### Gate 2: Technical Feasibility
- [x] Architecture supports all requirements
- [x] Technology choices enable required functionality
- [x] Performance requirements are achievable
- [x] Security requirements are achievable

### Gate 3: Resource Availability
- [x] Required technologies are available (python-jose, FastAPI middleware)
- [x] Required infrastructure is available (environment variables for secrets)
- [x] Required skills are available (JWT, middleware, FastAPI)
- [x] Timeline is realistic for authentication implementation

## Phase 0: Outline & Research

**Research Tasks:**
- Middleware vs dependency-based auth enforcement (resolved: middleware for consistent application)
- JWT payload structure and required claims (resolved: sub for user_id, exp for expiration, iat for issued-at)
- HTTP status codes for auth failures (resolved: 401 for unauthorized, 403 for forbidden)

**Deliverables:**
- research.md (resolves all clarifications)

## Phase 1: Design & Contracts

**Design Deliverables:**

### Authentication Flow Diagram
1. Client makes request with Authorization: Bearer {token} header
2. JWT middleware intercepts request
3. Middleware validates token signature against shared secret
4. Middleware checks token expiration
5. Middleware extracts user_id from token payload
6. Request proceeds with user_id in request context, or returns 401 error

### JWT Validation Middleware Design
- **Component:** jwt_bearer.py - Custom HTTPBearer scheme
- **Functionality:** Validates JWT tokens on each protected request
- **Integration:** Applied to all protected API routes via FastAPI dependency injection
- **Error Handling:** Returns 401 Unauthorized for invalid tokens

### User Identity Extraction Strategy
- **Method:** Extract user_id from JWT token payload (sub claim)
- **Storage:** Attach user_id to request context for downstream handlers
- **Verification:** Validate user_id corresponds to legitimate user in database
- **Access Control:** Use extracted user_id to filter task queries

### Data Model (data-model.md)
#### JWT Token Structure
- **Claims:**
  - sub (subject): user_id
  - exp (expiration): token expiration time
  - iat (issued at): token creation time
  - jti (JWT ID): optional unique identifier for future revocation
- **Algorithm:** HS256 (symmetric encryption with shared secret)

### API Contracts
#### New Endpoints (if needed):
**POST /auth/validate-token** (Internal use)
- **Description:** Validate JWT token and return user info
- **Request Headers:** Authorization: Bearer {token}
- **Response:** 200 OK `{ "user_id": integer, "valid": boolean, "expires_at": "datetime" }`
- **Errors:** 401 Unauthorized

#### Modified Existing Endpoints:
All existing task endpoints will now require Authorization header and enforce user isolation:
- **GET /api/v1/tasks** - Only return tasks belonging to authenticated user
- **POST /api/v1/tasks** - Assign new task to authenticated user
- **GET /api/v1/tasks/{task_id}** - Only allow access to tasks owned by authenticated user
- **PUT /api/v1/tasks/{task_id}** - Only allow updates to tasks owned by authenticated user
- **DELETE /api/v1/tasks/{task_id}** - Only allow deletion of tasks owned by authenticated user

**Response Format:**
All endpoints maintain existing JSON structure but with user isolation enforced.

**Error Format:**
- 401 Unauthorized: `{ "detail": "Could not validate credentials" }`
- 403 Forbidden: `{ "detail": "Access denied: insufficient permissions" }`
- 404 Not Found: `{ "detail": "Resource not found" }` (for resources owned by other users)

**Implementation Approach:**
- Create JWT utility functions for token creation/validation
- Implement FastAPI middleware/dependency for token validation
- Update existing task endpoints to enforce user isolation
- Add configuration for shared secrets via environment variables

## Phase 2: Implementation Plan

**Tasks:**

1. **Token Strategy**
   - Create JWT utility module with token creation and validation functions
   - Define JWT payload structure with required claims
   - Implement token signing and verification with shared secret
   - Set up environment variable configuration for shared secret

2. **Backend Verification**
   - Create JWT Bearer authentication class extending FastAPI's HTTPBearer
   - Implement token validation middleware
   - Add token expiration checking
   - Add signature verification using shared secret

3. **Enforcement**
   - Update existing task endpoints to require authentication
   - Implement user identity extraction from JWT tokens
   - Modify data access layer to enforce user isolation
   - Add authorization checks to all task operations

4. **Validation**
   - Create comprehensive test suite for authentication flows
   - Test requests without tokens → 401
   - Test requests with invalid tokens → 401
   - Test requests with mismatched user_id → 403/404
   - Test requests with valid tokens → succeed

## Phase 3: Validation & Testing

**Validation Approach:**
- Unit tests for JWT utility functions
- Integration tests for middleware functionality
- End-to-end tests for complete authentication flows
- Security tests for common vulnerabilities

**Success Criteria:**
- JWT tokens properly validated with signature and expiration checks
- Requests without tokens return 401 Unauthorized
- Requests with invalid tokens return 401 Unauthorized
- Requests with mismatched user_id are properly rejected
- Requests with valid tokens succeed with proper user isolation
- System meets performance and security requirements