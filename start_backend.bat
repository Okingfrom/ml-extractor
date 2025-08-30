@echo off
REM Start ML Extractor backend (run from repo root)
cd /d "%~dp0backend"
C:\Users\equipo\AppData\Local\Programs\Python\Python313\python.exe -m uvicorn dev_server:app --host 0.0.0.0 --port 8009
pause
