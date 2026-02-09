@echo off
REM Pre-flight Check Script - Verifies all prerequisites
REM Windows Version

echo ========================================
echo Pre-flight Check
echo ========================================
echo.
echo Checking if everything is ready to run...
echo.

set ERROR_COUNT=0

REM Check Python
echo [1/10] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo   [FAIL] Python not found! Install Python 3.11+
    set /a ERROR_COUNT+=1
) else (
    python --version
    echo   [PASS] Python found
)
echo.

REM Check Node.js
echo [2/10] Checking Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo   [FAIL] Node.js not found! Install Node.js 18+
    set /a ERROR_COUNT+=1
) else (
    node --version
    echo   [PASS] Node.js found
)
echo.

REM Check npm
echo [3/10] Checking npm...
npm --version >nul 2>&1
if errorlevel 1 (
    echo   [FAIL] npm not found!
    set /a ERROR_COUNT+=1
) else (
    npm --version
    echo   [PASS] npm found
)
echo.

REM Check backend directory
echo [4/10] Checking backend directory...
if not exist "backend" (
    echo   [FAIL] backend directory not found!
    set /a ERROR_COUNT+=1
) else (
    echo   [PASS] backend directory exists
)
echo.

REM Check frontend directory
echo [5/10] Checking frontend directory...
if not exist "frontend" (
    echo   [FAIL] frontend directory not found!
    set /a ERROR_COUNT+=1
) else (
    echo   [PASS] frontend directory exists
)
echo.

REM Check backend virtual environment
echo [6/10] Checking backend virtual environment...
if not exist "backend\venv" (
    echo   [FAIL] Virtual environment not found!
    echo   Run: cd backend ^&^& python -m venv venv
    set /a ERROR_COUNT+=1
) else (
    echo   [PASS] Virtual environment exists
)
echo.

REM Check backend dependencies
echo [7/10] Checking backend dependencies...
if not exist "backend\venv\Lib\site-packages\fastapi" (
    echo   [FAIL] Backend dependencies not installed!
    echo   Run: cd backend ^&^& venv\Scripts\activate ^&^& pip install -r requirements-chat.txt
    set /a ERROR_COUNT+=1
) else (
    echo   [PASS] Backend dependencies installed
)
echo.

REM Check frontend dependencies
echo [8/10] Checking frontend dependencies...
if not exist "frontend\node_modules" (
    echo   [FAIL] Frontend dependencies not installed!
    echo   Run: cd frontend ^&^& npm install
    set /a ERROR_COUNT+=1
) else (
    echo   [PASS] Frontend dependencies installed
)
echo.

REM Check backend .env
echo [9/10] Checking backend .env file...
if not exist "backend\.env" (
    echo   [FAIL] backend\.env not found!
    echo   Create backend\.env with DATABASE_URL and OPENAI_API_KEY
    set /a ERROR_COUNT+=1
) else (
    echo   [PASS] backend\.env exists

    REM Check for OPENAI_API_KEY
    findstr /C:"OPENAI_API_KEY=sk-" "backend\.env" >nul 2>&1
    if errorlevel 1 (
        echo   [WARN] OPENAI_API_KEY might not be set correctly
        echo   Make sure to add your OpenAI API key
    ) else (
        echo   [PASS] OPENAI_API_KEY appears to be set
    )
)
echo.

REM Check frontend .env.local
echo [10/10] Checking frontend .env.local file...
if not exist "frontend\.env.local" (
    echo   [WARN] frontend\.env.local not found (optional)
    echo   Will use default: http://localhost:8000
) else (
    echo   [PASS] frontend\.env.local exists
)
echo.

echo ========================================
echo Pre-flight Check Complete
echo ========================================
echo.

if %ERROR_COUNT% EQU 0 (
    echo [SUCCESS] All checks passed! Ready to start servers.
    echo.
    echo Run: start-all.bat
) else (
    echo [FAILED] %ERROR_COUNT% check(s) failed. Please fix the issues above.
)
echo.
pause
