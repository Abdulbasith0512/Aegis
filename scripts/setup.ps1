# AegisAI Developer Environment Setup Script (Windows PowerShell)
# ==============================================================================

Write-Host "Setting up AegisAI Developer Workspace..." -ForegroundColor Green

# 1. Verify Python Installation
if (Get-Command python -ErrorAction SilentlyContinue) {
    Write-Host "Python found: $(python --version)"
} else {
    Write-Warning "Python is not installed or not in system path. Please install Python 3.10+."
    exit 1
}

# 2. Verify Node.js Installation
if (Get-Command node -ErrorAction SilentlyContinue) {
    Write-Host "Node.js found: $(node --version)"
} else {
    Write-Warning "Node.js is not installed. Please install Node.js v18+ for the frontend."
    exit 1
}

# 3. Create Python Virtual Environment
if (-not (Test-Path -Path "backend\.venv")) {
    Write-Host "Creating Python virtual environment in backend\.venv..."
    python -m venv backend\.venv
} else {
    Write-Host "Virtual environment already exists."
}

# 4. Activate Venv and Install Dependencies
Write-Host "To activate virtual environment and install dependencies, run:" -ForegroundColor Yellow
Write-Host "  backend\.venv\Scripts\Activate.ps1"
Write-Host "  pip install -r backend\requirements.txt"

# 5. Env variables
if (-not (Test-Path -Path ".env")) {
    Write-Host "Copying .env.example to .env..."
    Copy-Item -Path ".env.example" -Destination ".env"
}

Write-Host "Setup Completed successfully." -ForegroundColor Green
