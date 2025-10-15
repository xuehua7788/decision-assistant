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
