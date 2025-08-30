@echo off
echo ======================================================
echo ML-Extractor Quick Start
echo ======================================================
echo.

REM Check if we're in the right directory
if not exist "frontend\package.json" (
    echo Error: Please run this from the ml-extractor directory
    pause
    exit /b 1
)

echo Starting development servers...
echo.
echo Frontend: http://localhost:3002
echo Backend:  http://localhost:8009/docs
echo.

REM Create virtual environment if needed
if not exist ".venv" (
    echo Creating Python environment...
    python -m venv .venv
)

REM Activate and install Python deps
echo Installing Python dependencies...
call .venv\Scripts\activate.bat
pip install -r requirements.txt >nul 2>&1

REM Install Node deps if needed
if not exist "frontend\node_modules" (
    echo Installing Node.js dependencies...
    cd frontend
    npm install >nul 2>&1
    cd ..
)

echo.
echo ======================================================
echo READY! Starting servers...
echo ======================================================
echo.

REM Start backend
echo Starting FastAPI backend...
start "Backend" cmd /c ".venv\Scripts\activate.bat && cd backend && python -m uvicorn main:app --reload --port 8009"

REM Wait a moment
timeout /t 3 >nul

REM Start frontend
echo Starting React frontend...
cd frontend
npm start
