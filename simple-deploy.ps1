Write-Host "Starting deployment..." -ForegroundColor Green

# Commit code
git add .
git commit -m "Fix deployment configuration"
git push origin main

Write-Host "Code pushed to GitHub" -ForegroundColor Green
Write-Host "Please check:" -ForegroundColor Yellow
Write-Host "- Vercel: https://vercel.com/dashboard" -ForegroundColor Cyan
Write-Host "- Render: https://dashboard.render.com" -ForegroundColor Cyan
Write-Host "Deployment complete!" -ForegroundColor Green

