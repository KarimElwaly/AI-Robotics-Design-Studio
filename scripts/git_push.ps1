# PowerShell script to commit and push to GitHub
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " COMMITTING AND PUSHING TO GITHUB" -ForegroundColor Cyan
Write-Host " Target: https://github.com/KarimElwaly/AI-Robotics-Design-Studio" -ForegroundColor White
Write-Host "==========================================================" -ForegroundColor Cyan

$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

# 1. Configure remote
git remote remove origin 2>$null
git remote add origin https://github.com/KarimElwaly/AI-Robotics-Design-Studio.git
Write-Host "`n[1/4] Remote origin configured." -ForegroundColor Green

# 2. Stage files
Write-Host "[2/4] Staging files..." -ForegroundColor Yellow
git add .

# 3. Commit
Write-Host "[3/4] Committing..." -ForegroundColor Yellow
git commit -m "feat: complete AI Robotics Design Studio platform implementation"

# 4. Push
Write-Host "[4/4] Setting main branch and pushing to origin..." -ForegroundColor Yellow
git branch -M main
git push -u origin main

Write-Host "`n>>> Successfully pushed to GitHub! <<<" -ForegroundColor Green
