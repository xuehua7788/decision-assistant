# 删除多余Vercel项目脚本
Write-Host "=== 删除多余的Vercel项目 ===" -ForegroundColor Red
Write-Host "保留: decision-assistant-frontend-prod" -ForegroundColor Green
Write-Host "删除: 其他所有项目" -ForegroundColor Yellow

# 要删除的项目列表
$projectsToDelete = @(
    "decision-assistant",
    "decision-assistant-bx", 
    "decision-assistant-65ie",
    "decision-assistant-d4n4",
    "decision-assistant-yxbl",
    "decision-assistant-kj8r",
    "decision-assistant-g6zm",
    "decision-assistant-79ca"
)

Write-Host "`n开始删除项目..." -ForegroundColor Yellow

foreach ($project in $projectsToDelete) {
    Write-Host "`n正在删除: $project" -ForegroundColor Cyan
    try {
        # 使用echo y来自动确认删除
        echo y | vercel project rm $project
        Write-Host "✅ 成功删除: $project" -ForegroundColor Green
    } catch {
        Write-Host "❌ 删除失败: $project - $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host "`n=== 删除完成 ===" -ForegroundColor Green
Write-Host "检查剩余项目..." -ForegroundColor Yellow
vercel project ls
