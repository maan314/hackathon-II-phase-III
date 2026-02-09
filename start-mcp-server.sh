#!/bin/bash

echo "========================================"
echo "Starting MCP Task Tooling Server"
echo "========================================"
echo ""
echo "Port: 8001"
echo "Environment: Development"
echo ""
echo "Press Ctrl+C to stop the server"
echo "========================================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Creating..."
    python -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies if needed
pip install -q -r backend/requirements.txt

# Run database migration
echo "Running database migrations..."
python -m backend.mcp.db.migrate

# Start server
echo ""
echo "Starting server..."
uvicorn backend.mcp.server:app --host 0.0.0.0 --port 8001 --reload
