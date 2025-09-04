# Quick Start Script for ML-Extractor Local Development
# This script starts both frontend and backend for local testing

Write-Host "======================================================" -ForegroundColor Blue
Write-Host "ML-Extractor Local Development Startup" -ForegroundColor Blue
Write-Host "======================================================" -ForegroundColor Blue
Write-Host ""

# Check if we're in the right directory
if (!(Test-Path "frontend\package.json") -or !(Test-Path "simple_backend.py")) {
    Write-Host "Error: Please run this script from the ml-extractor root directory" -ForegroundColor Red
    Write-Host "Current directory: $(Get-Location)" -ForegroundColor Yellow
    Write-Host "Expected files: frontend\package.json, simple_backend.py" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if Python virtual environment exists
if (!(Test-Path ".venv\Scripts\Activate.ps1")) {
    Write-Host "Creating Python virtual environment..." -ForegroundColor Yellow
    python -m venv .venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Error: Failed to create virtual environment" -ForegroundColor Red
        Write-Host "Make sure Python 3.8+ is installed and in PATH" -ForegroundColor Yellow
        Read-Host "Press Enter to exit"
        exit 1
    }
}

# Check if Node.js dependencies are installed
if (!(Test-Path "frontend\node_modules")) {
    Write-Host "Installing Node.js dependencies..." -ForegroundColor Yellow
    Set-Location frontend
    npm install
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Error: Failed to install Node.js dependencies" -ForegroundColor Red
        Write-Host "Make sure Node.js is installed and in PATH" -ForegroundColor Yellow
        Read-Host "Press Enter to exit"
        exit 1
    }
    Set-Location ..
}

# Install Python dependencies
Write-Host "Activating Python environment and installing dependencies..." -ForegroundColor Yellow
& .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt | Out-Null

Write-Host ""
Write-Host "======================================================" -ForegroundColor Green
Write-Host "Starting ML-Extractor Development Servers" -ForegroundColor Green
Write-Host "======================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Backend (FastAPI): http://localhost:8009" -ForegroundColor Cyan
Write-Host "API Documentation: http://localhost:8009/docs" -ForegroundColor Cyan
Write-Host "Frontend (React): http://localhost:3002" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop both servers" -ForegroundColor Yellow
Write-Host "======================================================" -ForegroundColor Green
Write-Host ""

# Function to start backend
$backendJob = Start-Job -ScriptBlock {
    Set-Location $using:PWD
    python -m uvicorn simple_backend:app --reload --host 0.0.0.0 --port 8009
}

Write-Host "Starting backend server..." -ForegroundColor Yellow

# Wait a moment for backend to start
Start-Sleep -Seconds 3

# Test if backend is running
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8009/health" -TimeoutSec 5 -ErrorAction SilentlyContinue
    if ($response.StatusCode -eq 200) {
        Write-Host "✓ Backend server started successfully" -ForegroundColor Green
    } else {
        Write-Host "⚠ Backend server may not be ready yet" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠ Backend server starting..." -ForegroundColor Yellow
}
}

# Start frontend
Write-Host "Starting frontend server..." -ForegroundColor Yellow
Set-Location frontend

try {
    # Start frontend server
    npm start
} finally {
    # Cleanup: Stop backend job when frontend stops
    Write-Host ""
    Write-Host "Shutting down servers..." -ForegroundColor Yellow
    
    # Stop backend job
    if ($backendJob) {
        Stop-Job $backendJob -ErrorAction SilentlyContinue
        Remove-Job $backendJob -ErrorAction SilentlyContinue
    }
    
    # Kill any remaining Python processes
    Get-Process -Name python -ErrorAction SilentlyContinue | Where-Object {$_.ProcessName -eq "python"} | Stop-Process -Force -ErrorAction SilentlyContinue
    
    Write-Host "Development servers stopped." -ForegroundColor Green
}

Read-Host "Press Enter to exit"
