# Hackathon II Phase III - Full Stack AI Task Management

**Status:** ✅ Ready to Run | **Integration:** Complete | **AI Agent:** Fully Functional

A full-stack application featuring AI-powered task management with natural language processing, integrated MCP tools, and a modern Next.js frontend.

---

## 🚀 Quick Start

### Start Backend Server
```bash
cd backend
start-backend.bat    # Windows
./start-backend.sh   # Linux/Mac
```

This starts:
- Main API Server on port 8000

### Start Frontend Server
```bash
cd frontend
start-frontend.bat   # Windows
./start-frontend.sh  # Linux/Mac
```

This starts the Next.js frontend on port 3000.

### Access Points
- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8001 (configured in frontend/.env.local)
---

## ⚠️ IMPORTANT: Configuration

**Backend `.env` is already configured with:**
- ✅ Database connection (Neon PostgreSQL)
- ✅ Cohere API key
- ✅ AI agent settings

**Frontend `.env.local` is already configured with:**
- ✅ Backend API URL: http://localhost:8001
- ✅ Chat API URL: http://localhost:8001

---

## 📁 Project Structure

```
hackathon-II-phase-III/
├── backend/                    # Python FastAPI Backend
│   ├── api/                   # API endpoints
│   ├── db/                    # Database models and CRUD
│   │   ├── models.py         # SQLModel definitions
│   │   ├── crud/             # CRUD operations
│   │   └── migrations/       # Database migrations
│   ├── mcp/                   # MCP Server (Task Tools)
│   │   ├── server.py         # MCP FastAPI server
│   │   ├── tools/            # Tool handlers
│   │   └── schemas/          # Pydantic schemas
│   ├── agent/                 # AI Agent Integration
│   │   ├── agent.py          # Cohere agent
│   │   ├── mcp_client.py     # MCP client
│   │   └── mcp_tools.py      # Tool definitions
│   ├── main.py               # Main API server
│   ├── config.py             # Configuration
│   ├── .env                  # Environment variables
│   └── requirements-chat.txt # Python dependencies
│
├── frontend/                  # Next.js Frontend
│   ├── app/                  # Next.js app directory
│   ├── components/           # React components
│   ├── lib/                  # Utilities
│   │   └── api-client.ts    # API client
│   ├── .env.local           # Frontend environment
│   └── package.json         # Node dependencies
│
├── specs/                    # Feature specifications
│   ├── 2-ai-chat-agent/     # AI Chat Agent spec
│   └── 3-mcp-task-tools/    # MCP Tools spec
│
├── history/                  # Prompt history records
│
├── .gitignore               # Git ignore rules
├── CLAUDE.md                # Claude Code project instructions
└── README.md                # This file
```

---

## 🎯 Features

### AI-Powered Task Management
- **Natural Language Processing:** Create, update, and manage tasks using conversational AI
- **MCP Tools Integration:** 5 stateless tools for task operations
- **Conversation Persistence:** All chats stored in Neon PostgreSQL
- **User Isolation:** Secure, per-user task management

### Backend Features
- **FastAPI REST API:** High-performance async API
- **Cohere Integration:** Command-R-Plus powered chat agent
- **MCP Server:** Model Context Protocol for tool calling
- **Database:** Neon PostgreSQL with SQLModel ORM
- **Stateless Architecture:** Horizontal scaling ready

### Frontend Features
- **Next.js 14:** Modern React framework
- **TypeScript:** Type-safe development
- **Tailwind CSS:** Utility-first styling
- **Better Auth:** Authentication system
- **Responsive Design:** Mobile-friendly UI

---

## 🛠️ Technology Stack

### Backend
- **Framework:** FastAPI 0.109.0
- **AI:** Cohere Command-R-Plus
- **ORM:** SQLModel 0.0.14
- **Database:** Neon PostgreSQL
- **Server:** Uvicorn (ASGI)
- **Language:** Python 3.11+

### Frontend
- **Framework:** Next.js 14.0.0
- **Language:** TypeScript 5.2.2
- **Styling:** Tailwind CSS 3.3.5
- **HTTP Client:** Axios 1.6.0
- **Auth:** Better Auth 1.4.18

### MCP Tools
- **Protocol:** Model Context Protocol
- **Tools:** add_task, list_tasks, complete_task, delete_task, update_task
- **Transport:** HTTP (FastAPI)
- **Validation:** Pydantic schemas

---

## 📋 Setup Instructions

### 1. Backend Setup

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

# Configure environment
# Edit .env and add your COHERE_API_KEY
```

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Environment already configured in .env.local
```

### 3. Database Migration

```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Run migrations
python -m backend.mcp.db.migrate
```

### 4. Start Servers

**Backend:**
```bash
cd backend
# Windows:
start-backend.bat
# Linux/Mac:
./start-backend.sh
```

**Frontend:**
```bash
cd frontend
# Windows:
start-frontend.bat
# Linux/Mac:
./start-frontend.sh
```

---

## 🧪 Testing the Integration

### Test Backend
```bash
curl http://localhost:8001/health
```

### Test AI Chat Agent
```bash
curl -X POST http://localhost:8001/api/test_user/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Create a task to review the proposal"
  }'
```

### Test Frontend
Open browser: http://localhost:3000

---

## 📚 Documentation

### Specifications
- **[specs/3-ai-chat-agent/](specs/3-ai-chat-agent/)** - AI Chat Agent specification and implementation details

---

## 🔧 Configuration

### Backend Environment Variables (`backend/.env`)
```bash
# Database (Already configured)
DATABASE_URL=postgresql://...

# Cohere (Already configured)
COHERE_API_KEY= ""

# AI Agent Configuration
AGENT_MODEL=command-r-08-2024
AGENT_TEMPERATURE=0.7
AGENT_MAX_TOKENS=1000
AGENT_TIMEOUT=60

# Application
ENVIRONMENT=development
LOG_LEVEL=INFO
```

### Frontend Environment Variables (`frontend/.env.local`)
```bash
# Backend API URL (Already configured)
NEXT_PUBLIC_API_URL=http://localhost:8001

# Chat API URL (Already configured)
NEXT_PUBLIC_CHAT_API_URL=http://localhost:8001
```

---

## 🌐 API Endpoints

### Backend API (Port 8001)
- `GET /` - Root endpoint
- `GET /health` - Health check
- `POST /api/{user_id}/chat` - AI Chat Agent with conversation persistence and tool calling
- `GET /api/{user_id}/todos` - List user tasks
- `POST /api/{user_id}/todos` - Create new task
- `PUT /api/{user_id}/todos/{todo_id}` - Update task
- `DELETE /api/{user_id}/todos/{todo_id}` - Delete task
- `GET /api/{user_id}/conversations` - List conversations
- `GET /api/{user_id}/conversations/{id}/messages` - Get messages

### AI Chat Agent Endpoint (NEW)

**Endpoint:** `POST /api/{user_id}/chat`

**Features:**
- Persistent conversation history across sessions
- Context-aware responses using conversation history
- Natural language task management via Cohere Command-R-Plus
- Automatic tool invocation for task operations
- User isolation and authentication

**Request:**
```json
{
  "message": "Add a task to buy groceries tomorrow",
  "conversation_id": "optional-uuid-for-continuing-conversation"
}
```

**Response:**
```json
{
  "response": "I've added 'Buy groceries' to your tasks for tomorrow",
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "message_id": "660e8400-e29b-41d4-a716-446655440001",
  "timestamp": "2026-02-09T21:00:00Z",
  "tool_calls": [
    {
      "tool_name": "add_task",
      "status": "success"
    }
  ]
}
```

**Example Usage:**
```bash
# Start new conversation
curl -X POST http://localhost:8000/api/user_123/chat \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "What tasks do I have?"}'

# Continue conversation
curl -X POST http://localhost:8000/api/user_123/chat \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Mark the first one as complete",
    "conversation_id": "550e8400-e29b-41d4-a716-446655440000"
  }'
```

### MCP Server (Port 8001)
- `GET /health` - Health check
- `GET /tools` - List available tools
- `POST /tools/add_task` - Create task
- `POST /tools/list_tasks` - List tasks
- `POST /tools/complete_task` - Complete task
- `POST /tools/delete_task` - Delete task
- `POST /tools/update_task` - Update task

---

## 💬 Natural Language Examples

The AI agent understands natural language for task management:

- "Create a task to review the proposal"
- "Show me my pending tasks"
- "Mark task 1 as complete"
- "Update task 2 title to 'Review Q4 proposal'"
- "Delete task 3"
- "What tasks do I have due this week?"

---

## 🐛 Troubleshooting

### Backend Won't Start
- **Missing Cohere API key:** Add to `backend/.env`
- **Port 8000 in use:** Kill existing process
- **Database connection failed:** Check DATABASE_URL

### Frontend Can't Connect
- **Backend not running:** Start backend first
- **Wrong API URL:** Check `frontend/.env.local`
- **CORS errors:** Verify backend CORS config

### MCP Server Issues
- **Port 8001 in use:** Kill existing process
- **Tools not working:** Check backend logs
- **Database errors:** Verify migrations ran

See [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md) for detailed troubleshooting.

---

## 📊 Port Configuration

| Service | Port | URL | Purpose |
|---------|------|-----|---------|
| Frontend | 3000 | http://localhost:3000 | Next.js UI |
| Backend API | 8000 | http://localhost:8000 | Main API + Chat |
| MCP Server | 8001 | http://localhost:8001 | Task Tools |

---

## 🚀 Deployment

### Development (Current Setup)
- Frontend: `npm run dev` (Port 3000)
- Backend: `uvicorn main:app --reload` (Port 8000)
- MCP: `uvicorn mcp.server:app --reload` (Port 8001)

### Production
- Update environment variables for production URLs
- Use `npm run build` for frontend
- Run backend with multiple workers: `--workers 4`
- Configure reverse proxy (nginx/Caddy) for HTTPS

---

## 🤝 Contributing

This is a hackathon project. For questions or issues:
1. Check documentation in `docs/` and `specs/`
2. Review implementation summaries
3. Check prompt history in `history/`

---

## 📝 License

Hackathon Project - Phase III

---

## 🎉 Ready to Start?

1. **Check prerequisites:** Run `preflight-check`
2. **Add Cohere API key:** Edit `backend/.env`
3. **Start all servers:** Run `start-all`
4. **Open browser:** http://localhost:3000

**Need help?** Check [QUICK_START.md](QUICK_START.md) for step-by-step instructions.

---

**Status:** ✅ Integration Complete | **Last Updated:** 2026-02-09 | **Version:** 1.0.0
