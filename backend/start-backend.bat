@echo off
REM Backend Startup Script for Windows
REM Starts both the main API server and MCP server

echo ========================================
echo Starting Backend Servers
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found!
    echo Please create one first: python -m venv venv
    echo Then install dependencies: pip install -r requirements-chat.txt
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if .env file exists
if not exist ".env" (
    echo ERROR: .env file not found!
    echo Please create .env file with required variables
    echo See .env.example for reference
    pause
    exit /b 1
)

echo.
echo Starting Main API Server on port 8000...
echo.
start "Backend API (Port 8000)" cmd /k "cd /d %~dp0 && venv\Scripts\activate.bat && python -m uvicorn main:app --reload --port 8000"

timeout /t 3 /nobreak >nul

echo.
echo Starting MCP Server on port 8001...
echo.
start "MCP Server (Port 8001)" cmd /k "cd /d %~dp0 && venv\Scripts\activate.bat && python -m uvicorn mcp.server:app --reload --port 8001"

echo.
echo ========================================
echo Backend servers are starting...
echo ========================================
echo.
echo Main API: http://localhost:8000
echo MCP Server: http://localhost:8001
echo.
echo Check the opened terminal windows for logs
echo Press any key to exit this window...
pause >nul
