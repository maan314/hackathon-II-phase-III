#!/bin/bash
# Master Startup Script - Starts Both Frontend and Backend
# Linux/Mac Version

echo "========================================"
echo "Starting Full Stack Application"
echo "========================================"
echo ""
echo "This will start:"
echo "  1. Backend API Server (Port 8000)"
echo "  2. MCP Server (Port 8001)"
echo "  3. Frontend Next.js (Port 3000)"
echo ""
echo "========================================"
echo ""

# Check prerequisites
echo "Checking prerequisites..."
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python not found! Please install Python 3.11+"
    exit 1
fi
echo "[OK] Python found"

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "ERROR: Node.js not found! Please install Node.js 18+"
    exit 1
fi
echo "[OK] Node.js found"

# Check backend virtual environment
if [ ! -d "backend/venv" ]; then
    echo "ERROR: Backend virtual environment not found!"
    echo "Please run: cd backend && python -m venv venv && pip install -r requirements-chat.txt"
    exit 1
fi
echo "[OK] Backend virtual environment found"

# Check frontend node_modules
if [ ! -d "frontend/node_modules" ]; then
    echo "ERROR: Frontend dependencies not installed!"
    echo "Please run: cd frontend && npm install"
    exit 1
fi
echo "[OK] Frontend dependencies found"

# Check backend .env
if [ ! -f "backend/.env" ]; then
    echo "ERROR: Backend .env file not found!"
    echo "Please create backend/.env with required variables"
    exit 1
fi
echo "[OK] Backend .env found"

# Check frontend .env.local
if [ ! -f "frontend/.env.local" ]; then
    echo "WARNING: Frontend .env.local not found, using defaults"
else
    echo "[OK] Frontend .env.local found"
fi

echo ""
echo "========================================"
echo "All prerequisites met!"
echo "========================================"
echo ""
echo "Starting servers..."
echo ""

# Start Backend in background
echo "Starting Backend servers..."
cd backend
./start-backend.sh &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 5

# Start Frontend in background
echo "Starting Frontend server..."
cd frontend
./start-frontend.sh &
FRONTEND_PID=$!
cd ..

echo ""
echo "========================================"
echo "All servers are running!"
echo "========================================"
echo ""
echo "Access points:"
echo "  Frontend:  http://localhost:3000"
echo "  Backend:   http://localhost:8000"
echo "  MCP:       http://localhost:8001"
echo ""
echo "Press Ctrl+C to stop all servers"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "Stopping all servers..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 0
}

trap cleanup INT TERM

# Wait for processes
wait $BACKEND_PID $FRONTEND_PID
