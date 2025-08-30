# Simple React + FastAPI Development Starter
# This is a simplified version that should work reliably

Write-Host "======================================================" -ForegroundColor Blue
Write-Host "ML-Extractor Development Startup (Simple)" -ForegroundColor Blue
Write-Host "======================================================" -ForegroundColor Blue

# Check if we're in the right directory
if (!(Test-Path "frontend\package.json")) {
    Write-Host "Error: Please run this from the ml-extractor directory" -ForegroundColor Red
    Write-Host "Current directory: $(Get-Location)" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "Starting ML-Extractor development servers..." -ForegroundColor Green
Write-Host ""
Write-Host "Frontend (React): http://localhost:3002" -ForegroundColor Cyan
Write-Host "Backend (FastAPI): http://localhost:8009" -ForegroundColor Cyan
Write-Host "API Docs: http://localhost:8009/docs" -ForegroundColor Cyan
Write-Host ""

# Create virtual environment if needed
if (!(Test-Path ".venv")) {
    Write-Host "Creating Python virtual environment..." -ForegroundColor Yellow
    python -m venv .venv
}

# Install Python dependencies
Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
& .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt | Out-Null

# Install Node dependencies if needed
if (!(Test-Path "frontend\node_modules")) {
    Write-Host "Installing Node.js dependencies..." -ForegroundColor Yellow
    Set-Location frontend
    npm install
    Set-Location ..
}

Write-Host "======================================================" -ForegroundColor Green
Write-Host "READY! Open these URLs in your browser:" -ForegroundColor Green
Write-Host "React UI: http://localhost:3002" -ForegroundColor White
Write-Host "API Docs: http://localhost:8009/docs" -ForegroundColor White
Write-Host "======================================================" -ForegroundColor Green
Write-Host ""

# Start backend in background
Write-Host "1. Starting FastAPI backend..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-Command", "cd '$PWD'; .\.venv\Scripts\Activate.ps1; cd backend; python -m uvicorn main:app --reload --port 8009" -WindowStyle Minimized

# Wait a bit
Start-Sleep 3

# Start frontend (this will open browser automatically)
Write-Host "2. Starting React frontend..." -ForegroundColor Yellow
Set-Location frontend
npm start
