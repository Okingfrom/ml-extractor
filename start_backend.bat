@echo off
REM Start ML Extractor backend (run from repo root)
cd /d "%~dp0"
echo 🚀 Starting ML Extractor Simple Backend on port 8009...
python -m uvicorn simple_backend:app --host 0.0.0.0 --port 8009 --reload
pause
