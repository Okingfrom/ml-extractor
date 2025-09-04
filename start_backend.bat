@echo off
REM Start ML Extractor backend (run from repo root)
REM Use the backend/main.py FastAPI app
cd /d "%~dp0"
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8009
pause
