Write-Host "Checking deployment status..." -ForegroundColor Green

Write-Host ""
Write-Host "Frontend (Vercel):" -ForegroundColor Yellow
Write-Host "Production URL: https://decision-assistant-kxqqlg6uc-bruces-projects-409b2d51.vercel.app" -ForegroundColor Cyan
Write-Host "Inspect: https://vercel.com/bruces-projects-409b2d51/decision-assistant" -ForegroundColor Cyan

Write-Host ""
Write-Host "Backend (Render):" -ForegroundColor Yellow
Write-Host "Expected URL: https://decision-assistant-api.onrender.com" -ForegroundColor Cyan
Write-Host "Dashboard: https://dashboard.render.com" -ForegroundColor Cyan

Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Go to Render Dashboard and redeploy backend" -ForegroundColor White
Write-Host "2. Set environment variable: OPENAI_API_KEY" -ForegroundColor White
Write-Host "3. Test backend health: https://decision-assistant-api.onrender.com/health" -ForegroundColor White
Write-Host "4. Test frontend connection" -ForegroundColor White

Write-Host ""
Write-Host "Environment variables needed:" -ForegroundColor Yellow
Write-Host "Render Backend:" -ForegroundColor Cyan
Write-Host "  - OPENAI_API_KEY=your-key" -ForegroundColor Gray
Write-Host "  - PORT=8000" -ForegroundColor Gray
Write-Host "  - FLASK_ENV=production" -ForegroundColor Gray

Write-Host ""
Write-Host "Deployment check complete!" -ForegroundColor Green

