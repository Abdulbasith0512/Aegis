# AegisAI Banking Simulator Execution Script (Windows PowerShell)
# ==============================================================================

Write-Host "AegisAI Simulation Engine bootstrapping..." -ForegroundColor Green

# 1. Run migrations to ensure all tables exist prior to simulation import
Write-Host "1. Running database migrations..." -ForegroundColor Yellow
$migResult = python -m alembic upgrade head
if ($LASTEXITCODE -ne 0) {
    Write-Warning "Migrations failed to run. Check if your PostgreSQL service is running and configured correctly in .env."
    # If migrations failed because tables already exist, it is fine to attempt simulation anyway.
} else {
    Write-Host "Database migrations completed successfully." -ForegroundColor Green
}

# 2. Start the simulator script
Write-Host "2. Running the simulator data generator..." -ForegroundColor Yellow
python scripts/banking_simulator.py

if ($LASTEXITCODE -eq 0) {
    Write-Host "AegisAI database seeding completed successfully." -ForegroundColor Green
} else {
    Write-Error "Simulation data ingestion failed. Review the logs above."
}
