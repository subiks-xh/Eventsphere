$ErrorActionPreference = 'Stop'

Write-Host "Setting up test environment..." -ForegroundColor Cyan

# Ensure we're in the right directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectDir = Split-Path -Parent $scriptDir
Set-Location $projectDir

# Activate virtual environment
if (Test-Path "venv\Scripts\activate.ps1") {
    . .\venv\Scripts\activate.ps1
} else {
    Write-Host "Warning: Virtual environment not found at venv\" -ForegroundColor Yellow
}

# Install pytest if not present
python -c "import pytest" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Installing pytest..." -ForegroundColor Cyan
    pip install pytest
}

# Run tests
Write-Host "Running pytest suite..." -ForegroundColor Green
$env:PYTHONPATH = "."
pytest tests/ -v

Write-Host "Test run complete." -ForegroundColor Cyan
