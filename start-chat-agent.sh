#!/bin/bash

echo "========================================"
echo "Starting AI Chat Agent Server (Phase III)"
echo "========================================"
echo ""
echo "Port: 8002"
echo "Your existing backend on port 8000 is NOT affected"
echo ""
echo "Press Ctrl+C to stop the server"
echo "========================================"
echo ""

cd backend
python chat_server.py
