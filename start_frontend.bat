@echo off
echo 🚀 Starting React Frontend for ML Extractor
echo 📁 Navigating to frontend directory...
cd /d "%~dp0frontend"
echo 📦 Starting React development server on port 3001...
set PORT=3001
npm start
