#!/bin/bash
# Pre-flight Check Script - Verifies all prerequisites
# Linux/Mac Version

echo "========================================"
echo "Pre-flight Check"
echo "========================================"
echo ""
echo "Checking if everything is ready to run..."
echo ""

ERROR_COUNT=0

# Check Python
echo "[1/10] Checking Python..."
if command -v python3 &> /dev/null; then
    python3 --version
    echo "  [PASS] Python found"
else
    echo "  [FAIL] Python not found! Install Python 3.11+"
    ((ERROR_COUNT++))
fi
echo ""

# Check Node.js
echo "[2/10] Checking Node.js..."
if command -v node &> /dev/null; then
    node --version
    echo "  [PASS] Node.js found"
else
    echo "  [FAIL] Node.js not found! Install Node.js 18+"
    ((ERROR_COUNT++))
fi
echo ""

# Check npm
echo "[3/10] Checking npm..."
if command -v npm &> /dev/null; then
    npm --version
    echo "  [PASS] npm found"
else
    echo "  [FAIL] npm not found!"
    ((ERROR_COUNT++))
fi
echo ""

# Check backend directory
echo "[4/10] Checking backend directory..."
if [ -d "backend" ]; then
    echo "  [PASS] backend directory exists"
else
    echo "  [FAIL] backend directory not found!"
    ((ERROR_COUNT++))
fi
echo ""

# Check frontend directory
echo "[5/10] Checking frontend directory..."
if [ -d "frontend" ]; then
    echo "  [PASS] frontend directory exists"
else
    echo "  [FAIL] frontend directory not found!"
    ((ERROR_COUNT++))
fi
echo ""

# Check backend virtual environment
echo "[6/10] Checking backend virtual environment..."
if [ -d "backend/venv" ]; then
    echo "  [PASS] Virtual environment exists"
else
    echo "  [FAIL] Virtual environment not found!"
    echo "  Run: cd backend && python3 -m venv venv"
    ((ERROR_COUNT++))
fi
echo ""

# Check backend dependencies
echo "[7/10] Checking backend dependencies..."
if [ -d "backend/venv/lib" ] && [ -n "$(find backend/venv/lib -name 'fastapi' 2>/dev/null)" ]; then
    echo "  [PASS] Backend dependencies installed"
else
    echo "  [FAIL] Backend dependencies not installed!"
    echo "  Run: cd backend && source venv/bin/activate && pip install -r requirements-chat.txt"
    ((ERROR_COUNT++))
fi
echo ""

# Check frontend dependencies
echo "[8/10] Checking frontend dependencies..."
if [ -d "frontend/node_modules" ]; then
    echo "  [PASS] Frontend dependencies installed"
else
    echo "  [FAIL] Frontend dependencies not installed!"
    echo "  Run: cd frontend && npm install"
    ((ERROR_COUNT++))
fi
echo ""

# Check backend .env
echo "[9/10] Checking backend .env file..."
if [ -f "backend/.env" ]; then
    echo "  [PASS] backend/.env exists"

    # Check for OPENAI_API_KEY
    if grep -q "OPENAI_API_KEY=sk-" "backend/.env"; then
        echo "  [PASS] OPENAI_API_KEY appears to be set"
    else
        echo "  [WARN] OPENAI_API_KEY might not be set correctly"
        echo "  Make sure to add your OpenAI API key"
    fi
else
    echo "  [FAIL] backend/.env not found!"
    echo "  Create backend/.env with DATABASE_URL and OPENAI_API_KEY"
    ((ERROR_COUNT++))
fi
echo ""

# Check frontend .env.local
echo "[10/10] Checking frontend .env.local file..."
if [ -f "frontend/.env.local" ]; then
    echo "  [PASS] frontend/.env.local exists"
else
    echo "  [WARN] frontend/.env.local not found (optional)"
    echo "  Will use default: http://localhost:8000"
fi
echo ""

echo "========================================"
echo "Pre-flight Check Complete"
echo "========================================"
echo ""

if [ $ERROR_COUNT -eq 0 ]; then
    echo "[SUCCESS] All checks passed! Ready to start servers."
    echo ""
    echo "Run: ./start-all.sh"
else
    echo "[FAILED] $ERROR_COUNT check(s) failed. Please fix the issues above."
fi
echo ""
