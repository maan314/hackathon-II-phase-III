#!/bin/bash
# Frontend Startup Script for Linux/Mac

echo "========================================"
echo "Starting Frontend Server"
echo "========================================"
echo ""

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "ERROR: node_modules not found!"
    echo "Please install dependencies first: npm install"
    exit 1
fi

# Check if .env.local exists
if [ ! -f ".env.local" ]; then
    echo "WARNING: .env.local file not found!"
    echo "Using default configuration..."
    echo ""
fi

echo "Starting Next.js development server on port 3000..."
echo ""
echo "Frontend will be available at: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

npm run dev
