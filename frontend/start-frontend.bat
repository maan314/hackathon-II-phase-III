@echo off
REM Frontend Startup Script for Windows

echo ========================================
echo Starting Frontend Server
echo ========================================
echo.

REM Check if node_modules exists
if not exist "node_modules" (
    echo ERROR: node_modules not found!
    echo Please install dependencies first: npm install
    pause
    exit /b 1
)

REM Check if .env.local exists
if not exist ".env.local" (
    echo WARNING: .env.local file not found!
    echo Using default configuration...
    echo.
)

echo Starting Next.js development server on port 3000...
echo.
echo Frontend will be available at: http://localhost:3000
echo.
echo Press Ctrl+C to stop the server
echo.

npm run dev
