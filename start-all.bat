@echo off
REM Master Startup Script - Starts Both Frontend and Backend
REM Windows Version

echo ========================================
echo Starting Full Stack Application
echo ========================================
echo.
echo This will start:
echo   1. Backend API Server (Port 8000)
echo   2. MCP Server (Port 8001)
echo   3. Frontend Next.js (Port 3000)
echo.
echo ========================================
echo.

REM Check prerequisites
echo Checking prerequisites...
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found! Please install Python 3.11+
    pause
    exit /b 1
)
echo [OK] Python found

REM Check Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js not found! Please install Node.js 18+
    pause
    exit /b 1
)
echo [OK] Node.js found

REM Check backend virtual environment
if not exist "backend\venv\Scripts\activate.bat" (
    echo ERROR: Backend virtual environment not found!
    echo Please run: cd backend && python -m venv venv && pip install -r requirements-chat.txt
    pause
    exit /b 1
)
echo [OK] Backend virtual environment found

REM Check frontend node_modules
if not exist "frontend\node_modules" (
    echo ERROR: Frontend dependencies not installed!
    echo Please run: cd frontend && npm install
    pause
    exit /b 1
)
echo [OK] Frontend dependencies found

REM Check backend .env
if not exist "backend\.env" (
    echo ERROR: Backend .env file not found!
    echo Please create backend\.env with required variables
    pause
    exit /b 1
)
echo [OK] Backend .env found

REM Check frontend .env.local
if not exist "frontend\.env.local" (
    echo WARNING: Frontend .env.local not found, using defaults
) else (
    echo [OK] Frontend .env.local found
)

echo.
echo ========================================
echo All prerequisites met!
echo ========================================
echo.
echo Starting servers...
echo.

REM Start Backend (opens in new window)
echo Starting Backend servers...
start "Backend Servers" cmd /c "cd /d %~dp0backend && start-backend.bat"

REM Wait a bit for backend to start
timeout /t 5 /nobreak >nul

REM Start Frontend (opens in new window)
echo Starting Frontend server...
start "Frontend Server" cmd /c "cd /d %~dp0frontend && start-frontend.bat"

echo.
echo ========================================
echo All servers are starting!
echo ========================================
echo.
echo Check the opened terminal windows for logs
echo.
echo Access points:
echo   Frontend:  http://localhost:3000
echo   Backend:   http://localhost:8000
echo   MCP:       http://localhost:8001
echo.
echo To stop servers: Close the terminal windows or press Ctrl+C in each
echo.
echo Press any key to exit this window...
pause >nul
