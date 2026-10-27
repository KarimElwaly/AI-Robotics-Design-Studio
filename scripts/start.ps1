# PowerShell Startup Script for AI Robotics Design Studio
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " STARTING AI ROBOTICS DESIGN STUDIO (SW 2024 + 2026)" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

$Root = Split-Path -Parent $PSScriptRoot

# 1. Start FastAPI Backend (:8000)
Write-Host "`n[1/2] Launching FastAPI Backend on http://localhost:8000..." -ForegroundColor Yellow
$BackendJob = Start-Process -FilePath "python" -ArgumentList "-m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload" -WorkingDirectory $Root -PassThru

# 2. Check and Start Vite Frontend (:5173)
$FrontendDir = Join-Path $Root "frontend"
$NodeModules = Join-Path $FrontendDir "node_modules"
if (-not (Test-Path $NodeModules)) {
    Write-Host "[INFO] Installing frontend dependencies (one-time setup)..." -ForegroundColor Cyan
    Start-Process -FilePath "cmd.exe" -ArgumentList "/c npm install" -WorkingDirectory $FrontendDir -Wait
}

Write-Host "[2/2] Launching Vite Frontend on http://localhost:5173..." -ForegroundColor Yellow
$FrontendJob = Start-Process -FilePath "cmd.exe" -ArgumentList "/k npm run dev" -WorkingDirectory $FrontendDir -PassThru

Write-Host "`n>>> AI Robotics Design Studio is Running! <<<" -ForegroundColor Green
Write-Host "Frontend: http://localhost:5173" -ForegroundColor White
Write-Host "Backend API: http://localhost:8000/docs" -ForegroundColor White
Write-Host "Press Ctrl+C or close the windows to stop." -ForegroundColor Gray
