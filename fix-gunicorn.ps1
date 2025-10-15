# Fix Gunicorn Configuration
Write-Host "=== Fixing Gunicorn Configuration ===" -ForegroundColor Cyan

Write-Host "[1/3] Creating wsgi.py entry point..." -ForegroundColor Yellow
$wsgiContent = @'
"""
WSGI entry point for Gunicorn
"""
from app import app

if __name__ == "__main__":
    app.run()
'@
Set-Content -Path "backend/wsgi.py" -Value $wsgiContent -Encoding UTF8
Write-Host "OK wsgi.py created" -ForegroundColor Green

Write-Host "[2/3] Committing changes..." -ForegroundColor Yellow
git add .
git commit -m "Fix Gunicorn: Add wsgi.py entry point and update start command"
git push origin main
Write-Host "OK Changes pushed to GitHub" -ForegroundColor Green

Write-Host "[3/3] Configuration summary..." -ForegroundColor Yellow
Write-Host ""
Write-Host "Updated Render Configuration:" -ForegroundColor Cyan
Write-Host "  Start Command: gunicorn --bind 0.0.0.0:`$PORT wsgi:app" -ForegroundColor White
Write-Host "  Entry Point: backend/wsgi.py" -ForegroundColor White
Write-Host ""
Write-Host "In Render Dashboard, update Start Command to:" -ForegroundColor Yellow
Write-Host "  gunicorn --bind 0.0.0.0:`$PORT wsgi:app" -ForegroundColor Cyan
Write-Host ""
Write-Host "Or simply use:" -ForegroundColor Yellow
Write-Host "  gunicorn wsgi:app" -ForegroundColor Cyan
Write-Host ""
Write-Host "=== Fix Complete! ===" -ForegroundColor Green
Write-Host "Redeploy in Render Dashboard to apply changes" -ForegroundColor Yellow

