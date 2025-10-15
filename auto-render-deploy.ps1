# Render Backend Automated Deployment Script
Write-Host "=== Starting Render Automated Deployment Configuration ===" -ForegroundColor Cyan
Write-Host "Execution time: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Gray

# Check directory
if (-not (Test-Path "backend/app.py")) {
    Write-Host "Error: Please run from project root directory" -ForegroundColor Red
    exit 1
}

# 1. Configure backend requirements.txt
Write-Host ""
Write-Host "[1/8] Creating requirements.txt..." -ForegroundColor Yellow
$requirements = @"
Flask==2.3.3
Flask-CORS==4.0.0
python-dotenv==1.0.0
openai==1.3.0
gunicorn==21.2.0
Werkzeug==2.3.7
"@
Set-Content -Path "backend/requirements.txt" -Value $requirements -Encoding UTF8
Write-Host "OK requirements.txt created" -ForegroundColor Green

# 2. Create render.yaml
Write-Host "[2/8] Creating render.yaml..." -ForegroundColor Yellow
$renderYaml = @"
services:
  - type: web
    name: decision-assistant-api
    env: python
    region: oregon
    plan: free
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn app:app
    envVars:
      - key: PYTHON_VERSION
        value: 3.9.0
"@
Set-Content -Path "render.yaml" -Value $renderYaml -Encoding UTF8
Write-Host "OK render.yaml created" -ForegroundColor Green

# 3. Create build.sh
Write-Host "[3/8] Creating build.sh..." -ForegroundColor Yellow
$buildScript = @"
#!/usr/bin/env bash
set -o errexit
pip install --upgrade pip
pip install -r requirements.txt
"@
Set-Content -Path "backend/build.sh" -Value $buildScript -Encoding UTF8
Write-Host "OK build.sh created" -ForegroundColor Green

# 4. Create .env.example
Write-Host "[4/8] Creating .env.example..." -ForegroundColor Yellow
$envExample = @"
OPENAI_API_KEY=sk-your-openai-api-key-here
PORT=8000
FLASK_ENV=production
"@
Set-Content -Path "backend/.env.example" -Value $envExample -Encoding UTF8
Write-Host "OK .env.example created" -ForegroundColor Green

# 5. Update frontend configuration
Write-Host "[5/8] Configuring frontend environment..." -ForegroundColor Yellow
$frontendEnvProd = "VITE_API_URL=https://decision-assistant-api.onrender.com"
Set-Content -Path "frontend/.env.production" -Value $frontendEnvProd -Encoding UTF8

if (-not (Test-Path "frontend/src/config")) {
    New-Item -ItemType Directory -Path "frontend/src/config" -Force | Out-Null
}

$apiConfig = @"
const API_BASE_URL = import.meta.env.VITE_API_URL || 
  (import.meta.env.MODE === 'production'
    ? 'https://decision-assistant-api.onrender.com'
    : 'http://localhost:8000');
export default API_BASE_URL;
"@
Set-Content -Path "frontend/src/config/api.js" -Value $apiConfig -Encoding UTF8
Write-Host "OK Frontend configuration updated" -ForegroundColor Green

# 6. Git commit
Write-Host "[6/8] Committing code to GitHub..." -ForegroundColor Yellow
git add .
git commit -m "Configure backend for Render deployment with auto script"
git push origin main
Write-Host "OK Code pushed" -ForegroundColor Green

# 7. Create test script
Write-Host "[7/8] Creating test script..." -ForegroundColor Yellow
$testScript = @'
Write-Host "Testing Render API..." -ForegroundColor Cyan
$apiUrl = "https://decision-assistant-api.onrender.com"
try {
    $response = Invoke-RestMethod -Uri "$apiUrl/health" -TimeoutSec 10
    Write-Host "OK API is running normally" -ForegroundColor Green
    Write-Host "Response: $($response | ConvertTo-Json)" -ForegroundColor Gray
} catch {
    Write-Host "API is deploying, please try again later" -ForegroundColor Yellow
    Write-Host "Check status at: https://dashboard.render.com" -ForegroundColor Cyan
}
'@
Set-Content -Path "test-api.ps1" -Value $testScript -Encoding UTF8
Write-Host "OK Test script created: test-api.ps1" -ForegroundColor Green

# 8. Open browser
Write-Host "[8/8] Opening Render Dashboard..." -ForegroundColor Yellow
Start-Process "https://dashboard.render.com/new/web"

Write-Host ""
Write-Host "=== All automated tasks completed! ===" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps in browser:" -ForegroundColor Yellow
Write-Host "  1. Connect GitHub: xuehua7788/decision-assistant" -ForegroundColor White
Write-Host "  2. Root Directory: backend" -ForegroundColor White
Write-Host "  3. Build Command: pip install -r requirements.txt" -ForegroundColor White
Write-Host "  4. Start Command: gunicorn app:app" -ForegroundColor White
Write-Host "  5. Add environment variable: OPENAI_API_KEY" -ForegroundColor Yellow
Write-Host ""
Write-Host "Test after deployment:" -ForegroundColor Cyan
Write-Host "  powershell -File test-api.ps1" -ForegroundColor White

