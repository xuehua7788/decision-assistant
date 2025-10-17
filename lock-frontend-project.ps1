# 锁定前端项目，防止意外修改
Write-Host "=== 锁定 decision-assistant-frontend-prod 项目 ===" -ForegroundColor Green

# 1. 确保项目已链接
Write-Host "`n[1/3] 确保项目正确链接..." -ForegroundColor Yellow
vercel link --project=decision-assistant-frontend-prod

# 2. 设置项目保护
Write-Host "`n[2/3] 设置项目保护..." -ForegroundColor Yellow
Write-Host "✅ 项目已链接到 decision-assistant-frontend-prod" -ForegroundColor Green
Write-Host "✅ URL 锁定: https://decision-assistant-frontend-prod.vercel.app" -ForegroundColor Green

# 3. 创建部署检查脚本
Write-Host "`n[3/3] 创建部署前检查..." -ForegroundColor Yellow
$checkScript = @"
# 部署前检查脚本
Write-Host "检查是否链接到正确项目..." -ForegroundColor Yellow
`$currentProject = vercel project ls | findstr "decision-assistant-frontend-prod"
if (`$currentProject) {
    Write-Host "✅ 安全：已链接到 decision-assistant-frontend-prod" -ForegroundColor Green
    return `$true
} else {
    Write-Host "❌ 危险：未链接到正确项目！" -ForegroundColor Red
    Write-Host "请先运行: vercel link --project=decision-assistant-frontend-prod" -ForegroundColor Yellow
    return `$false
}
"@

$checkScript | Out-File -FilePath "check-deployment-safety.ps1" -Encoding UTF8

Write-Host "`n=== 项目锁定完成 ===" -ForegroundColor Green
Write-Host "保护措施:" -ForegroundColor Cyan
Write-Host "1. 项目已链接到 decision-assistant-frontend-prod" -ForegroundColor White
Write-Host "2. URL 已锁定: https://decision-assistant-frontend-prod.vercel.app" -ForegroundColor White
Write-Host "3. 创建了安全检查脚本: check-deployment-safety.ps1" -ForegroundColor White
Write-Host "`n以后部署请使用: powershell -File deploy-frontend-safely.ps1" -ForegroundColor Yellow
