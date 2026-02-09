# Frontend and Backend Integration Guide

## Quick Start - Run Both Servers

This guide will help you start both the frontend and backend servers together.

## Prerequisites

### Backend Requirements
- Python 3.11+
- Virtual environment activated
- Dependencies installed: `pip install -r backend/requirements-chat.txt`

### Frontend Requirements
- Node.js 18+
- Dependencies installed: `npm install` (in frontend directory)

### Required Environment Variables

**Backend (.env file already configured):**
- ✅ DATABASE_URL - Neon PostgreSQL connection
- ⚠️ OPENAI_API_KEY - **YOU NEED TO ADD YOUR OPENAI API KEY**
- ✅ ENVIRONMENT=development
- ✅ LOG_LEVEL=INFO

**Frontend (.env.local already configured):**
- ✅ NEXT_PUBLIC_API_URL=http://localhost:8000
- ✅ NEXT_PUBLIC_MCP_URL=http://localhost:8001

## Configuration Summary

### ✅ What's Already Configured

1. **Frontend API Client** - Points to `http://localhost:8000`
2. **Backend CORS** - Allows `http://localhost:3000`
3. **Database Connection** - Neon PostgreSQL configured
4. **Environment Variables** - Set up for local development

### ⚠️ What You Need to Do

**IMPORTANT: Add your OpenAI API key to backend/.env**

Edit `backend/.env` and replace:
```
OPENAI_API_KEY=sk-proj-your-openai-api-key-here
```

With your actual OpenAI API key from https://platform.openai.com/api-keys

## Starting the Servers

### Option 1: Manual Start (Recommended for First Time)

**Terminal 1 - Backend (Todo API + AI Chat Agent):**
```bash
cd backend
python -m uvicorn main:app --reload --port 8000
```

**Terminal 2 - MCP Server (Task Management Tools):**
```bash
cd backend
python -m uvicorn mcp.server:app --reload --port 8001
```

**Terminal 3 - Frontend (Next.js):**
```bash
cd frontend
npm run dev
```

### Option 2: Using Startup Scripts (After First Successful Run)

**Windows:**
```bash
# Start backend
start-backend.bat

# Start frontend
start-frontend.bat
```

**Linux/Mac:**
```bash
# Start backend
./start-backend.sh

# Start frontend
./start-frontend.sh
```

## Verify Everything is Running

### 1. Backend Health Check
```bash
curl http://localhost:8000/health
```
Expected: `{"status": "healthy", "database": "connected"}`

### 2. MCP Server Health Check
```bash
curl http://localhost:8001/health
```
Expected: `{"status": "healthy", "timestamp": "...", "service": "mcp-task-server"}`

### 3. Frontend
Open browser: http://localhost:3000

## API Endpoints Available

### Backend (Port 8000)
- `GET /` - Root endpoint
- `GET /health` - Health check
- `POST /api/{user_id}/chat` - Chat without MCP tools
- `POST /api/{user_id}/chat_mcp` - Chat with MCP tools (AI task management)
- `GET /api/{user_id}/conversations` - List conversations
- `GET /api/{user_id}/conversations/{id}/messages` - Get messages

### MCP Server (Port 8001)
- `GET /health` - Health check
- `GET /tools` - List available tools
- `POST /tools/add_task` - Create task
- `POST /tools/list_tasks` - List tasks
- `POST /tools/complete_task` - Complete task
- `POST /tools/delete_task` - Delete task
- `POST /tools/update_task` - Update task

### Frontend (Port 3000)
- `http://localhost:3000` - Main application

## Testing the Integration

### Test 1: Backend Connection
```bash
curl http://localhost:8000/health
```

### Test 2: MCP Tools
```bash
curl -X POST http://localhost:8001/tools/add_task \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test_user", "title": "Test task"}'
```

### Test 3: AI Chat with Task Management
```bash
curl -X POST http://localhost:8000/api/test_user/chat_mcp \
  -H "Content-Type: application/json" \
  -d '{"message": "Create a task to review the proposal", "enable_mcp_tools": true}'
```

### Test 4: Frontend
1. Open http://localhost:3000
2. Frontend should connect to backend automatically
3. Check browser console for any errors

## Troubleshooting

### Backend Won't Start
- **Error: "DATABASE_URL environment variable is required"**
  - Check `backend/.env` file exists
  - Verify DATABASE_URL is set

- **Error: "OPENAI_API_KEY environment variable is required"**
  - Add your OpenAI API key to `backend/.env`

### Frontend Can't Connect to Backend
- **Error: "Network Error" or "CORS Error"**
  - Verify backend is running on port 8000
  - Check CORS configuration in `backend/main.py`
  - Ensure `NEXT_PUBLIC_API_URL=http://localhost:8000` in `frontend/.env.local`

### MCP Server Issues
- **Port 8001 already in use**
  - Kill existing process: `lsof -ti:8001 | xargs kill -9` (Mac/Linux)
  - Or use different port in startup command

### Database Connection Issues
- **Error: "could not connect to server"**
  - Verify Neon database is active
  - Check DATABASE_URL format
  - Ensure SSL mode is set: `?sslmode=require`

## Port Configuration

| Service | Port | URL |
|---------|------|-----|
| Frontend | 3000 | http://localhost:3000 |
| Backend API | 8000 | http://localhost:8000 |
| MCP Server | 8001 | http://localhost:8001 |

## Development Workflow

1. **Start Backend First** - Ensures API is ready
2. **Start MCP Server** - Enables AI task management
3. **Start Frontend Last** - Connects to running backend

## Production Deployment Notes

For production deployment, update:

**Frontend (.env.production):**
```
NEXT_PUBLIC_API_URL=https://your-backend-domain.com
NEXT_PUBLIC_MCP_URL=https://your-mcp-domain.com
```

**Backend (.env):**
```
ENVIRONMENT=production
LOG_LEVEL=WARNING
```

**CORS Configuration:**
Update `backend/main.py` to include production frontend URL.

## Need Help?

- Backend logs: Check terminal running uvicorn
- Frontend logs: Check browser console (F12)
- MCP Server logs: Check terminal running MCP server
- Database: Check Neon dashboard

---

**Status:** ✅ Configuration Complete
**Last Updated:** 2026-02-09
