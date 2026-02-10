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
echo "Starting Main API Server (with integrated MCP) on port 8001..."
echo ""
python -m uvicorn main:app --reload --port 8001 &
API_PID=$!

echo ""
echo "========================================"
echo "Backend server is running"
echo "========================================"
echo ""
echo "Main API: http://localhost:8001 (PID: $API_PID)"
echo "(MCP tools are integrated into the main API)"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Wait for the process
wait $API_PID
