@echo off
echo ========================================
echo Starting MCP Task Tooling Server
echo ========================================
echo.
echo Port: 8001
echo Environment: Development
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo Virtual environment not found. Creating...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate

REM Install dependencies if needed
pip install -q -r backend\requirements.txt

REM Run database migration
echo Running database migrations...
python -m backend.mcp.db.migrate

REM Start server
echo.
echo Starting server...
uvicorn backend.mcp.server:app --host 0.0.0.0 --port 8001 --reload

pause
