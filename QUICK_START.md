# 🚀 Quick Start Guide - Frontend + Backend Integration

## ⚡ Super Quick Start (For Impatient Developers)

**Windows:**
```bash
# 1. Check everything is ready
preflight-check.bat

# 2. Start all servers
start-all.bat
```

**Linux/Mac:**
```bash
# 1. Check everything is ready
./preflight-check.sh

# 2. Start all servers
./start-all.sh
```

**Access:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- MCP Server: http://localhost:8001

---

## 📋 Prerequisites Checklist

Before starting, make sure you have:

- [ ] Python 3.11+ installed
- [ ] Node.js 18+ installed
- [ ] Backend virtual environment created
- [ ] Backend dependencies installed
- [ ] Frontend dependencies installed
- [ ] Backend .env file configured
- [ ] **OpenAI API key added to backend/.env**

---

## 🔧 First Time Setup

### Step 1: Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements-chat.txt

# Verify .env file exists and has OPENAI_API_KEY
# Edit backend/.env and add your OpenAI API key
```

### Step 2: Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Verify .env.local exists (already configured)
```

### Step 3: Database Migration (First Time Only)

```bash
cd backend

# Activate virtual environment first
# Windows: venv\Scripts\activate
# Linux/Mac: source venv/bin/activate

# Run migrations
python -m backend.mcp.db.migrate
```

---

## 🎯 Starting the Servers

### Option 1: All-in-One (Recommended)

**Windows:**
```bash
start-all.bat
```

**Linux/Mac:**
```bash
./start-all.sh
```

This will start:
1. Backend API (Port 8000)
2. MCP Server (Port 8001)
3. Frontend (Port 3000)

### Option 2: Manual Start (For Debugging)

**Terminal 1 - Backend API:**
```bash
cd backend
# Windows: venv\Scripts\activate
# Linux/Mac: source venv/bin/activate
python -m uvicorn main:app --reload --port 8000
```

**Terminal 2 - MCP Server:**
```bash
cd backend
# Windows: venv\Scripts\activate
# Linux/Mac: source venv/bin/activate
python -m uvicorn mcp.server:app --reload --port 8001
```

**Terminal 3 - Frontend:**
```bash
cd frontend
npm run dev
```

---

## ✅ Verification Steps

### 1. Check Backend Health
```bash
curl http://localhost:8000/health
```
Expected: `{"status": "healthy", "database": "connected"}`

### 2. Check MCP Server Health
```bash
curl http://localhost:8001/health
```
Expected: `{"status": "healthy", ...}`

### 3. Check Frontend
Open browser: http://localhost:3000

### 4. Test Integration
```bash
curl -X POST http://localhost:8000/api/test_user/chat_mcp \
  -H "Content-Type: application/json" \
  -d '{"message": "Create a task to test the system", "enable_mcp_tools": true}'
```

---

## 🔍 Troubleshooting

### Backend Won't Start

**Error: "OPENAI_API_KEY environment variable is required"**
- Solution: Add your OpenAI API key to `backend/.env`
- Get key from: https://platform.openai.com/api-keys

**Error: "DATABASE_URL environment variable is required"**
- Solution: Verify `backend/.env` has DATABASE_URL
- Already configured with Neon PostgreSQL

**Error: "Port 8000 already in use"**
- Solution: Kill existing process
  - Windows: `netstat -ano | findstr :8000` then `taskkill /PID <pid> /F`
  - Linux/Mac: `lsof -ti:8000 | xargs kill -9`

### Frontend Won't Start

**Error: "Cannot connect to backend"**
- Solution: Verify backend is running on port 8000
- Check `frontend/.env.local` has `NEXT_PUBLIC_API_URL=http://localhost:8000`

**Error: "Port 3000 already in use"**
- Solution: Kill existing process or use different port
  - `npm run dev -- -p 3001`

### MCP Server Issues

**Error: "Port 8001 already in use"**
- Solution: Kill existing process
  - Windows: `netstat -ano | findstr :8001` then `taskkill /PID <pid> /F`
  - Linux/Mac: `lsof -ti:8001 | xargs kill -9`

---

## 📊 Port Configuration

| Service | Port | URL | Purpose |
|---------|------|-----|---------|
| Frontend | 3000 | http://localhost:3000 | Next.js UI |
| Backend API | 8000 | http://localhost:8000 | Main API + Chat |
| MCP Server | 8001 | http://localhost:8001 | Task Management Tools |

---

## 🎨 What You Can Do

### Via Frontend (http://localhost:3000)
- User authentication
- Todo management
- AI chat interface

### Via Backend API (http://localhost:8000)
- `/health` - Health check
- `/api/{user_id}/chat` - Chat without tools
- `/api/{user_id}/chat_mcp` - Chat with AI task management
- `/api/{user_id}/conversations` - List conversations

### Via MCP Server (http://localhost:8001)
- `/tools/add_task` - Create tasks
- `/tools/list_tasks` - List tasks
- `/tools/complete_task` - Complete tasks
- `/tools/delete_task` - Delete tasks
- `/tools/update_task` - Update tasks

---

## 🧪 Testing the Integration

### Test 1: Basic Backend
```bash
curl http://localhost:8000/health
```

### Test 2: MCP Tools
```bash
curl -X POST http://localhost:8001/tools/add_task \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test", "title": "My first task"}'
```

### Test 3: AI Chat with Task Management
```bash
curl -X POST http://localhost:8000/api/test_user/chat_mcp \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Create a task to review the proposal",
    "enable_mcp_tools": true
  }'
```

### Test 4: Frontend
1. Open http://localhost:3000
2. Check browser console (F12) for errors
3. Verify API calls go to localhost:8000

---

## 📝 Configuration Files

### Backend Configuration
- `backend/.env` - Environment variables (DATABASE_URL, OPENAI_API_KEY)
- `backend/config.py` - Configuration loader
- `backend/main.py` - Main API server
- `backend/mcp/server.py` - MCP server

### Frontend Configuration
- `frontend/.env.local` - Environment variables (NEXT_PUBLIC_API_URL)
- `frontend/lib/api-client.ts` - API client configuration
- `frontend/next.config.js` - Next.js configuration

---

## 🛠️ Development Tips

### Hot Reload
All servers support hot reload:
- Backend: Changes to Python files auto-reload
- MCP Server: Changes to Python files auto-reload
- Frontend: Changes to React/Next.js files auto-reload

### Logs
- Backend logs: Terminal running uvicorn (port 8000)
- MCP logs: Terminal running MCP server (port 8001)
- Frontend logs: Browser console (F12)

### Debugging
- Backend: Add `print()` statements or use debugger
- Frontend: Use browser DevTools (F12)
- API calls: Check Network tab in browser

---

## 🚨 Important Notes

### ⚠️ REQUIRED: OpenAI API Key
You MUST add your OpenAI API key to `backend/.env`:
```
OPENAI_API_KEY=sk-proj-your-actual-key-here
```

Without this, the AI chat features won't work!

### Database
- Already configured with Neon PostgreSQL
- Connection string in `backend/.env`
- Migrations run automatically on first start

### CORS
- Backend allows requests from `http://localhost:3000`
- Frontend sends requests to `http://localhost:8000`
- Configured for local development

---

## 📚 Additional Resources

- **Integration Guide:** `INTEGRATION_GUIDE.md`
- **MCP Server README:** `backend/mcp/README.md`
- **Implementation Summary:** `IMPLEMENTATION_SUMMARY.md`
- **MCP Validation:** `MCP_VALIDATION_CHECKLIST.md`

---

## 🎉 Success Indicators

You'll know everything is working when:

✅ Backend health check returns "healthy"
✅ MCP server health check returns "healthy"
✅ Frontend loads at http://localhost:3000
✅ No errors in browser console
✅ Can create tasks via AI chat
✅ Can see tasks in frontend

---

## 💡 Quick Commands Reference

```bash
# Check if ready
preflight-check.bat  # Windows
./preflight-check.sh # Linux/Mac

# Start everything
start-all.bat        # Windows
./start-all.sh       # Linux/Mac

# Start backend only
cd backend && start-backend.bat        # Windows
cd backend && ./start-backend.sh       # Linux/Mac

# Start frontend only
cd frontend && start-frontend.bat      # Windows
cd frontend && ./start-frontend.sh     # Linux/Mac

# Health checks
curl http://localhost:8000/health      # Backend
curl http://localhost:8001/health      # MCP Server
```

---

**Ready to start?** Run `preflight-check` first, then `start-all`!

**Need help?** Check `INTEGRATION_GUIDE.md` for detailed troubleshooting.
