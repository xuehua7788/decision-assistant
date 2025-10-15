# Test Render API
$apiUrl = "https://decision-assistant-api.onrender.com"

Write-Host "Testing API connection..." -ForegroundColor Yellow
Write-Host "API URL: $apiUrl" -ForegroundColor Cyan
Write-Host ""

try {
    # Test health check
    Write-Host "1. Testing /health endpoint..." -ForegroundColor White
    $health = Invoke-RestMethod -Uri "$apiUrl/health" -Method Get
    Write-Host "   OK Health check: $($health.status)" -ForegroundColor Green
    
    # Test main endpoint
    Write-Host "2. Testing / endpoint..." -ForegroundColor White
    $status = Invoke-RestMethod -Uri "$apiUrl/" -Method Get
    Write-Host "   OK API status: $($status.status)" -ForegroundColor Green
    Write-Host "   Version: $($status.version)" -ForegroundColor Gray
    
    Write-Host ""
    Write-Host "=== API Deployment Successful! ===" -ForegroundColor Green
    Write-Host "Frontend URL: https://decision-assistant-kxqqlg6uc-bruces-projects-409b2d51.vercel.app" -ForegroundColor Cyan
    Write-Host "Backend URL: $apiUrl" -ForegroundColor Cyan
}
catch {
    Write-Host "   ERROR API not ready yet" -ForegroundColor Red
    Write-Host ""
    Write-Host "Possible reasons:" -ForegroundColor Yellow
    Write-Host "  - Render is still deploying (wait 3-5 minutes)" -ForegroundColor White
    Write-Host "  - Service not created yet" -ForegroundColor White
    Write-Host "  - Wrong service URL" -ForegroundColor White
    Write-Host ""
    Write-Host "Check deployment status: https://dashboard.render.com" -ForegroundColor Cyan
}

