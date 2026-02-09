# Hackathon II Phase III - Full Stack AI Task Management

**Status:** ✅ Ready to Run | **Integration:** Complete | **Documentation:** Comprehensive

A full-stack application featuring AI-powered task management with natural language processing, MCP (Model Context Protocol) tools, and a modern Next.js frontend.

---

## 🚀 Quick Start

### Prerequisites Check
```bash
# Windows
preflight-check.bat

# Linux/Mac
./preflight-check.sh
```

### Start All Servers
```bash
# Windows
start-all.bat

# Linux/Mac
./start-all.sh
```

### Access Points
- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **MCP Server:** http://localhost:8001

---

## ⚠️ IMPORTANT: Before Starting

**You MUST add your OpenAI API key to `backend/.env`:**

```bash
OPENAI_API_KEY=sk-proj-your-actual-openai-api-key-here
```

Get your API key from: https://platform.openai.com/api-keys

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
│   │   ├── agent.py          # OpenAI agent
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
├── start-all.bat            # Windows: Start all servers
├── start-all.sh             # Linux/Mac: Start all servers
├── preflight-check.bat      # Windows: Prerequisites check
├── preflight-check.sh       # Linux/Mac: Prerequisites check
├── QUICK_START.md           # Quick start guide
├── INTEGRATION_GUIDE.md     # Detailed integration guide
└── INTEGRATION_COMPLETE.md  # Integration summary
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
- **OpenAI Integration:** GPT-4 powered chat agent
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
- **AI:** OpenAI GPT-4
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
# Edit .env and add your OPENAI_API_KEY
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

```bash
# From project root
# Windows:
start-all.bat

# Linux/Mac:
./start-all.sh
```

---

## 🧪 Testing the Integration

### Test Backend
```bash
curl http://localhost:8000/health
```

### Test MCP Server
```bash
curl http://localhost:8001/health
```

### Test AI Task Management
```bash
curl -X POST http://localhost:8000/api/test_user/chat_mcp \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Create a task to review the proposal",
    "enable_mcp_tools": true
  }'
```

### Test Frontend
Open browser: http://localhost:3000

---

## 📚 Documentation

### Quick References
- **[QUICK_START.md](QUICK_START.md)** - Get started in 5 minutes
- **[INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md)** - Detailed setup and troubleshooting
- **[INTEGRATION_COMPLETE.md](INTEGRATION_COMPLETE.md)** - Integration summary

### Implementation Details
- **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** - MCP server implementation
- **[backend/mcp/README.md](backend/mcp/README.md)** - MCP server documentation
- **[MCP_VALIDATION_CHECKLIST.md](MCP_VALIDATION_CHECKLIST.md)** - Validation guide

### Specifications
- **[specs/2-ai-chat-agent/](specs/2-ai-chat-agent/)** - AI Chat Agent spec
- **[specs/3-mcp-task-tools/](specs/3-mcp-task-tools/)** - MCP Tools spec

---

## 🔧 Configuration

### Backend Environment Variables (`backend/.env`)
```bash
# Database (Already configured)
DATABASE_URL=postgresql://...

# OpenAI (YOU MUST ADD THIS)
OPENAI_API_KEY=sk-proj-your-key-here

# Application
ENVIRONMENT=development
LOG_LEVEL=INFO
API_TIMEOUT=10
```

### Frontend Environment Variables (`frontend/.env.local`)
```bash
# Backend API URL (Already configured)
NEXT_PUBLIC_API_URL=http://localhost:8000

# MCP Server URL (Already configured)
NEXT_PUBLIC_MCP_URL=http://localhost:8001
```

---

## 🌐 API Endpoints

### Backend API (Port 8000)
- `GET /` - Root endpoint
- `GET /health` - Health check
- `POST /api/{user_id}/chat` - **NEW: AI Chat Agent with conversation persistence**
- `POST /api/{user_id}/chat_mcp` - Chat with MCP tools
- `GET /api/{user_id}/conversations` - List conversations
- `GET /api/{user_id}/conversations/{id}/messages` - Get messages

### AI Chat Agent Endpoint (NEW)

**Endpoint:** `POST /api/{user_id}/chat`

**Features:**
- Persistent conversation history across sessions
- Context-aware responses using conversation history
- Natural language task management via OpenAI GPT-4
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
- **Missing OpenAI API key:** Add to `backend/.env`
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
2. **Add OpenAI API key:** Edit `backend/.env`
3. **Start all servers:** Run `start-all`
4. **Open browser:** http://localhost:3000

**Need help?** Check [QUICK_START.md](QUICK_START.md) for step-by-step instructions.

---

**Status:** ✅ Integration Complete | **Last Updated:** 2026-02-09 | **Version:** 1.0.0
