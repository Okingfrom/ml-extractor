@echo off
echo 🚀 Starting React Frontend for ML Extractor
echo 📁 Navigating to frontend directory...
cd /d "%~dp0frontend"
echo 📦 Starting React development server on port 3002...
set PORT=3002
npm start
