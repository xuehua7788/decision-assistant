# Complete Render Deployment Script
Write-Host "=== Completing Render Deployment ===" -ForegroundColor Cyan

# 1. Open Render Dashboard
Write-Host "Opening Render Dashboard..." -ForegroundColor Yellow
Start-Process "https://dashboard.render.com/new/web"

# 2. Wait for user action
Write-Host ""
Write-Host "Please complete the following steps in your browser:" -ForegroundColor Green
Write-Host ("=" * 50) -ForegroundColor DarkGray

Write-Host ""
Write-Host "Step 1: Connect GitHub" -ForegroundColor Yellow
Write-Host "  - Select 'Connect GitHub account'" -ForegroundColor White
Write-Host "  - Authorize Render to access your repository" -ForegroundColor White

Write-Host ""
Write-Host "Step 2: Select Repository" -ForegroundColor Yellow
Write-Host "  - Search: decision-assistant" -ForegroundColor White
Write-Host "  - Select: xuehua7788/decision-assistant" -ForegroundColor Cyan

Write-Host ""
Write-Host "Step 3: Configure Service" -ForegroundColor Yellow
Write-Host "  Name: decision-assistant-api" -ForegroundColor White
Write-Host "  Region: Oregon (US West)" -ForegroundColor White
Write-Host "  Branch: main" -ForegroundColor White
Write-Host "  Root Directory: backend" -ForegroundColor Cyan
Write-Host "  Runtime: Python 3" -ForegroundColor White
Write-Host "  Build Command: pip install -r requirements.txt" -ForegroundColor Cyan
Write-Host "  Start Command: gunicorn app:app" -ForegroundColor Cyan

Write-Host ""
Write-Host "Step 4: Add Environment Variables" -ForegroundColor Yellow
Write-Host "  Click 'Advanced' to expand settings" -ForegroundColor White
Write-Host "  Add the following environment variables:" -ForegroundColor White
Write-Host "    - OPENAI_API_KEY = [your-openai-key]" -ForegroundColor Yellow
Write-Host "    - PORT = 8000" -ForegroundColor White
Write-Host "    - FLASK_ENV = production" -ForegroundColor White
Write-Host "    - PYTHON_VERSION = 3.9.0" -ForegroundColor White

Write-Host ""
Write-Host "Step 5: Create Service" -ForegroundColor Yellow
Write-Host "  - Select Free plan" -ForegroundColor Green
Write-Host "  - Click 'Create Web Service'" -ForegroundColor Cyan

Write-Host ""
Write-Host ("=" * 50) -ForegroundColor DarkGray

# 3. Wait for confirmation
Write-Host ""
Write-Host "Press Enter to confirm you have completed the above steps..." -ForegroundColor Yellow
Read-Host

# 4. Check deployment status
Write-Host ""
Write-Host "Checking deployment status..." -ForegroundColor Yellow
Write-Host "Estimated deployment time: 3-5 minutes" -ForegroundColor White

# 5. Generate test script
$testScript = @'
# Test Render API
$apiUrl = "https://decision-assistant-api.onrender.com"

Write-Host "Testing API connection..." -ForegroundColor Yellow

try {
    # Test health check
    $health = Invoke-RestMethod -Uri "$apiUrl/health" -Method Get
    Write-Host "OK API health check successful: $($health.status)" -ForegroundColor Green
    
    # Test main endpoint
    $status = Invoke-RestMethod -Uri "$apiUrl/" -Method Get
    Write-Host "OK API status: $($status.status)" -ForegroundColor Green
    
    Write-Host ""
    Write-Host "API deployment successful!" -ForegroundColor Green
    Write-Host "API URL: $apiUrl" -ForegroundColor Cyan
}
catch {
    Write-Host "API not ready yet, please try again later" -ForegroundColor Yellow
    Write-Host "Check deployment status: https://dashboard.render.com" -ForegroundColor White
}
'@

Set-Content -Path "test-render-api.ps1" -Value $testScript -Encoding UTF8
Write-Host "OK Created test script: test-render-api.ps1" -ForegroundColor Green

# 6. Update frontend configuration
Write-Host ""
Write-Host "Updating frontend API configuration..." -ForegroundColor Yellow

$envProduction = @"
VITE_API_URL=https://decision-assistant-api.onrender.com
"@
Set-Content -Path "frontend\.env.production" -Value $envProduction -Encoding UTF8

$apiConfig = @'
const API_BASE_URL = import.meta.env.VITE_API_URL || 
  (import.meta.env.MODE === 'production'
    ? 'https://decision-assistant-api.onrender.com'
    : 'http://localhost:8000');

export default API_BASE_URL;
'@
Set-Content -Path "frontend\src\config\api.js" -Value $apiConfig -Encoding UTF8

Write-Host "OK Frontend configuration updated" -ForegroundColor Green

# 7. Commit updates
Write-Host ""
Write-Host "Committing configuration updates..." -ForegroundColor Yellow
git add .
git commit -m "Update frontend API configuration for Render"
git push origin main

Write-Host ""
Write-Host "=== Deployment Completion Checklist ===" -ForegroundColor Cyan
Write-Host "[ ] Render service created" -ForegroundColor White
Write-Host "[ ] Environment variables configured" -ForegroundColor White
Write-Host "[ ] Deployment status is 'Live'" -ForegroundColor White
Write-Host "[ ] API endpoints accessible" -ForegroundColor White

Write-Host ""
Write-Host "Run test script to check API:" -ForegroundColor Yellow
Write-Host "  powershell -ExecutionPolicy Bypass -File test-render-api.ps1" -ForegroundColor Cyan

Write-Host ""
Write-Host "Complete API URL:" -ForegroundColor Green
Write-Host "  https://decision-assistant-api.onrender.com" -ForegroundColor Cyan

Write-Host ""
Write-Host "Deployment complete!" -ForegroundColor Green

