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
echo Starting Main API Server (with integrated MCP) on port 8001...
echo.
start "Backend API (Port 8001)" cmd /k "cd /d %~dp0 && venv\Scripts\activate.bat && python -m uvicorn main:app --reload --port 8001"

echo.
echo ========================================
echo Backend server is starting...
echo ========================================
echo.
echo Main API: http://localhost:8001
echo (MCP tools are integrated into the main API)
echo.
echo Check the opened terminal windows for logs
echo Press any key to exit this window...
pause >nul
