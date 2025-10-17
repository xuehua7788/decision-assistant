# 保护 decision-assistant-frontend-prod 项目脚本
Write-Host "=== 保护前端项目 ===" -ForegroundColor Green

# 1. 检查 decision-assistant-frontend-prod 状态
Write-Host "`n[1/4] 检查 decision-assistant-frontend-prod 状态..." -ForegroundColor Yellow
vercel project inspect decision-assistant-frontend-prod

# 2. 测试前端是否正常工作
Write-Host "`n[2/4] 测试前端访问..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "https://decision-assistant-frontend-prod.vercel.app" -UseBasicParsing
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ 前端正常访问" -ForegroundColor Green
    } else {
        Write-Host "❌ 前端访问异常: $($response.StatusCode)" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ 前端访问失败: $($_.Exception.Message)" -ForegroundColor Red
}

# 3. 显示所有项目列表
Write-Host "`n[3/4] 当前所有项目:" -ForegroundColor Yellow
vercel project ls

# 4. 提供删除建议
Write-Host "`n[4/4] 建议删除的多余项目:" -ForegroundColor Yellow
Write-Host "以下项目可以安全删除（保留 decision-assistant-frontend-prod）:" -ForegroundColor Cyan
Write-Host "- decision-assistant" -ForegroundColor Red
Write-Host "- decision-assistant-bx" -ForegroundColor Red
Write-Host "- decision-assistant-65ie" -ForegroundColor Red
Write-Host "- decision-assistant-d4n4" -ForegroundColor Red
Write-Host "- decision-assistant-yxbl" -ForegroundColor Red
Write-Host "- decision-assistant-kj8r" -ForegroundColor Red
Write-Host "- decision-assistant-g6zm" -ForegroundColor Red
Write-Host "- decision-assistant-79ca" -ForegroundColor Red

Write-Host "`n=== 保护完成 ===" -ForegroundColor Green
Write-Host "要删除多余项目，请手动运行:" -ForegroundColor Yellow
Write-Host "vercel project rm [项目名]" -ForegroundColor Cyan
