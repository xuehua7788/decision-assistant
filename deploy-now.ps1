# Decision Assistant Deployment Script
# Auto deploy to Vercel and Render

Write-Host "Starting deployment..." -ForegroundColor Green

# Check Git status
Write-Host "Checking Git status..." -ForegroundColor Yellow
$gitStatus = git status --porcelain
if ($gitStatus) {
    Write-Host "Uncommitted changes found, please commit first" -ForegroundColor Red
    Write-Host $gitStatus
    exit 1
}
Write-Host "Git status clean" -ForegroundColor Green

# Push to GitHub
Write-Host "Pushing to GitHub..." -ForegroundColor Yellow
git push origin main
if ($LASTEXITCODE -ne 0) {
    Write-Host "Push failed" -ForegroundColor Red
    exit 1
}
Write-Host "Code pushed to GitHub successfully" -ForegroundColor Green

# Deploy frontend to Vercel
Write-Host "Deploying frontend to Vercel..." -ForegroundColor Yellow
Set-Location frontend
try {
    # Check Vercel CLI
    $vercelVersion = vercel --version 2>$null
    if (-not $vercelVersion) {
        Write-Host "Installing Vercel CLI..." -ForegroundColor Yellow
        npm install -g vercel
    }
    
    # Deploy to production
    Write-Host "Deploying to Vercel production..." -ForegroundColor Yellow
    vercel --prod --yes
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Frontend deployment successful" -ForegroundColor Green
    } else {
        Write-Host "Frontend deployment may have issues, check Vercel Dashboard" -ForegroundColor Yellow
    }
} catch {
    Write-Host "Vercel deployment encountered issues: $($_.Exception.Message)" -ForegroundColor Yellow
    Write-Host "Please manually redeploy in Vercel Dashboard" -ForegroundColor Yellow
}

Set-Location ..

# Show deployment info
Write-Host ""
Write-Host "Deployment completed!" -ForegroundColor Green
Write-Host ("=" * 50) -ForegroundColor Cyan
Write-Host "Frontend: Check Vercel Dashboard" -ForegroundColor White
Write-Host "Backend: Check Render Dashboard" -ForegroundColor White
Write-Host "Environment variables:" -ForegroundColor White
Write-Host "   Vercel: REACT_APP_API_URL=https://your-render-url" -ForegroundColor Gray
Write-Host "   Render: OPENAI_API_KEY=your-openai-key" -ForegroundColor Gray
Write-Host ("=" * 50) -ForegroundColor Cyan

Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Redeploy backend in Render" -ForegroundColor White
Write-Host "2. Add environment variables in Vercel" -ForegroundColor White
Write-Host "3. Test frontend-backend connection" -ForegroundColor White

Write-Host ""
Write-Host "Deployment script completed!" -ForegroundColor Green
