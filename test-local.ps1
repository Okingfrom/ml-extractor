# Test Local Development Setup
# This script verifies that the local development environment is working

Write-Host "======================================================" -ForegroundColor Blue
Write-Host "ML-Extractor Local Development Test" -ForegroundColor Blue
Write-Host "======================================================" -ForegroundColor Blue
Write-Host ""

# Check prerequisites
Write-Host "Checking prerequisites..." -ForegroundColor Yellow

# Test Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python not found or not in PATH" -ForegroundColor Red
    $hasErrors = $true
}

# Test Node.js
try {
    $nodeVersion = node --version 2>&1
    Write-Host "✓ Node.js: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Node.js not found or not in PATH" -ForegroundColor Red
    $hasErrors = $true
}

# Test npm
try {
    $npmVersion = npm --version 2>&1
    Write-Host "✓ npm: v$npmVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ npm not found" -ForegroundColor Red
    $hasErrors = $true
}

Write-Host ""

# Check project structure
Write-Host "Checking project structure..." -ForegroundColor Yellow

$requiredFiles = @(
    "frontend\package.json",
    "backend\main.py",
    "requirements.txt",
    ".gitignore"
)

foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host "✓ $file exists" -ForegroundColor Green
    } else {
        Write-Host "✗ $file missing" -ForegroundColor Red
        $hasErrors = $true
    }
}

Write-Host ""

# Check Python virtual environment
Write-Host "Checking Python environment..." -ForegroundColor Yellow

if (Test-Path ".venv") {
    Write-Host "✓ Virtual environment exists" -ForegroundColor Green
    
    # Test activation
    try {
        & .\.venv\Scripts\Activate.ps1
        Write-Host "✓ Virtual environment can be activated" -ForegroundColor Green
        
        # Test key packages
        $packages = @("fastapi", "uvicorn", "pandas", "openpyxl")
        foreach ($package in $packages) {
            try {
                pip show $package | Out-Null
                Write-Host "✓ Python package: $package" -ForegroundColor Green
            } catch {
                Write-Host "⚠ Python package missing: $package" -ForegroundColor Yellow
                $hasWarnings = $true
            }
        }
    } catch {
        Write-Host "✗ Cannot activate virtual environment" -ForegroundColor Red
        $hasErrors = $true
    }
} else {
    Write-Host "⚠ Virtual environment not found - will be created on first run" -ForegroundColor Yellow
    $hasWarnings = $true
}

Write-Host ""

# Check Node.js dependencies
Write-Host "Checking Node.js dependencies..." -ForegroundColor Yellow

if (Test-Path "frontend\node_modules") {
    Write-Host "✓ Node.js dependencies installed" -ForegroundColor Green
    
    # Check key packages
    $nodePackages = @("react", "react-scripts", "axios", "tailwindcss")
    foreach ($package in $nodePackages) {
        if (Test-Path "frontend\node_modules\$package") {
            Write-Host "✓ Node.js package: $package" -ForegroundColor Green
        } else {
            Write-Host "⚠ Node.js package missing: $package" -ForegroundColor Yellow
            $hasWarnings = $true
        }
    }
} else {
    Write-Host "⚠ Node.js dependencies not installed - run 'npm install' in frontend directory" -ForegroundColor Yellow
    $hasWarnings = $true
}

Write-Host ""

# Test port availability
Write-Host "Checking port availability..." -ForegroundColor Yellow

$ports = @(3002, 8009, 5000)
foreach ($port in $ports) {
    try {
        $connection = Test-NetConnection -ComputerName localhost -Port $port -ErrorAction SilentlyContinue -WarningAction SilentlyContinue
        if ($connection.TcpTestSucceeded) {
            Write-Host "⚠ Port $port is in use" -ForegroundColor Yellow
            $hasWarnings = $true
        } else {
            Write-Host "✓ Port $port is available" -ForegroundColor Green
        }
    } catch {
        Write-Host "✓ Port $port is available" -ForegroundColor Green
    }
}

Write-Host ""

# Summary
Write-Host "======================================================" -ForegroundColor Blue
Write-Host "Test Summary" -ForegroundColor Blue
Write-Host "======================================================" -ForegroundColor Blue

if ($hasErrors) {
    Write-Host "✗ Setup has critical issues that need to be resolved" -ForegroundColor Red
    Write-Host ""
    Write-Host "To fix issues:" -ForegroundColor Yellow
    Write-Host "1. Install Python 3.8+ and add to PATH" -ForegroundColor White
    Write-Host "2. Install Node.js 16+ and add to PATH" -ForegroundColor White
    Write-Host "3. Run setup commands from the project directory" -ForegroundColor White
} elseif ($hasWarnings) {
    Write-Host "⚠ Setup is mostly ready but has some warnings" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "To complete setup:" -ForegroundColor Yellow
    Write-Host "1. Run: .\start-dev.ps1 (will install missing dependencies)" -ForegroundColor White
    Write-Host "2. Or manually run: python -m venv .venv && npm install" -ForegroundColor White
} else {
    Write-Host "✓ Setup is ready for local development!" -ForegroundColor Green
    Write-Host ""
    Write-Host "To start development:" -ForegroundColor Yellow
    Write-Host "1. Run: .\start-dev.ps1" -ForegroundColor White
    Write-Host "2. Open: http://localhost:3002 (frontend)" -ForegroundColor White
    Write-Host "3. Open: http://localhost:8009/docs (API docs)" -ForegroundColor White
}

Write-Host ""
Write-Host "Quick start commands:" -ForegroundColor Cyan
Write-Host "  .\start-dev.ps1        # Start both frontend and backend" -ForegroundColor White
Write-Host "  .\start-dev.bat        # Alternative batch file" -ForegroundColor White
Write-Host "  .\test-local.ps1       # Run this test again" -ForegroundColor White

Write-Host ""
Read-Host "Press Enter to exit"
