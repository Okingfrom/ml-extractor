@echo off
REM Quick Start Script for ML-Extractor Local Development
REM This script starts both frontend and backend for local testing

echo ======================================================
echo ML-Extractor Local Development Startup
echo ======================================================
echo.

REM Check if we're in the right directory
if not exist "frontend\package.json" (
    echo Error: Please run this script from the ml-extractor root directory
    echo Current directory: %CD%
    echo Expected files: frontend\package.json, backend\main.py
    pause
    exit /b 1
)

REM Check if Python virtual environment exists
if not exist ".venv\Scripts\activate.bat" (
    echo Creating Python virtual environment...
    python -m venv .venv
    if %ERRORLEVEL% neq 0 (
        echo Error: Failed to create virtual environment
        echo Make sure Python 3.8+ is installed
        pause
        exit /b 1
    )
)

REM Check if Node.js dependencies are installed
if not exist "frontend\node_modules" (
    echo Installing Node.js dependencies...
    cd frontend
    npm install
    if %ERRORLEVEL% neq 0 (
        echo Error: Failed to install Node.js dependencies
        echo Make sure Node.js is installed
        pause
        exit /b 1
    )
    cd ..
)

REM Install Python dependencies if needed
echo Activating Python environment and installing dependencies...
call .venv\Scripts\activate.bat
pip install -r requirements.txt >nul 2>&1

echo.
echo ======================================================
echo Starting ML-Extractor Development Servers
echo ======================================================
echo.
echo Backend (FastAPI): http://localhost:8009
echo API Documentation: http://localhost:8009/docs
echo Frontend (React): http://localhost:3002
echo.
echo Press Ctrl+C to stop both servers
echo ======================================================
echo.

REM Start backend in background
echo Starting backend server...
start "ML-Extractor Backend" cmd /c "cd backend && ..\\.venv\\Scripts\\activate.bat && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8009"

REM Wait a moment for backend to start
timeout /t 3 >nul

REM Start frontend
echo Starting frontend server...
cd frontend
npm start

REM When frontend closes, try to close backend window
echo.
echo Shutting down servers...
taskkill /f /im python.exe 2>nul
echo Development servers stopped.
pause
