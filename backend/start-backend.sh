#!/bin/bash
# Backend Startup Script for Linux/Mac
# Starts both the main API server and MCP server

echo "========================================"
echo "Starting Backend Servers"
echo "========================================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "ERROR: Virtual environment not found!"
    echo "Please create one first: python -m venv venv"
    echo "Then install dependencies: pip install -r requirements-chat.txt"
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "ERROR: .env file not found!"
    echo "Please create .env file with required variables"
    echo "See .env.example for reference"
    exit 1
fi

echo ""
echo "Starting Main API Server on port 8000..."
echo ""
python -m uvicorn main:app --reload --port 8000 &
API_PID=$!

sleep 3

echo ""
echo "Starting MCP Server on port 8001..."
echo ""
python -m uvicorn mcp.server:app --reload --port 8001 &
MCP_PID=$!

echo ""
echo "========================================"
echo "Backend servers are running"
echo "========================================"
echo ""
echo "Main API: http://localhost:8000 (PID: $API_PID)"
echo "MCP Server: http://localhost:8001 (PID: $MCP_PID)"
echo ""
echo "Press Ctrl+C to stop all servers"
echo ""

# Wait for both processes
wait $API_PID $MCP_PID
