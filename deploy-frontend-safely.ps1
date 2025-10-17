# 安全部署前端脚本 - 避免创建多个项目
Write-Host "=== 安全部署前端到 decision-assistant-frontend-prod ===" -ForegroundColor Green

# 1. 检查当前目录是否已链接到正确项目
Write-Host "`n[1/4] 检查项目链接状态..." -ForegroundColor Yellow
$currentProject = vercel project ls | findstr "decision-assistant-frontend-prod"
if ($currentProject) {
    Write-Host "✅ 已链接到 decision-assistant-frontend-prod" -ForegroundColor Green
} else {
    Write-Host "⚠️  未链接到正确项目，正在重新链接..." -ForegroundColor Yellow
    vercel link --project=decision-assistant-frontend-prod
}

# 2. 确认部署到正确项目
Write-Host "`n[2/4] 确认部署目标..." -ForegroundColor Yellow
Write-Host "目标项目: decision-assistant-frontend-prod" -ForegroundColor Cyan
Write-Host "目标URL: https://decision-assistant-frontend-prod.vercel.app" -ForegroundColor Cyan

# 3. 安全部署（不会创建新项目）
Write-Host "`n[3/4] 开始安全部署..." -ForegroundColor Yellow
Write-Host "使用 --prod 标志部署到生产环境..." -ForegroundColor Cyan
vercel --prod

# 4. 验证部署结果
Write-Host "`n[4/4] 验证部署结果..." -ForegroundColor Yellow
Write-Host "检查前端是否正常访问..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "https://decision-assistant-frontend-prod.vercel.app" -UseBasicParsing
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ 前端部署成功，正常访问" -ForegroundColor Green
    } else {
        Write-Host "❌ 前端访问异常: $($response.StatusCode)" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ 前端访问失败: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n=== 安全部署完成 ===" -ForegroundColor Green
Write-Host "前端地址: https://decision-assistant-frontend-prod.vercel.app" -ForegroundColor Cyan
