# 用户画像系统测试脚本（PowerShell）

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "用户画像系统测试" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

# 从Render获取的数据库连接信息
$env:DATABASE_URL = "postgresql://decision_user:YOUR_PASSWORD@dpg-d3otin3ipnbc739gk7g-a.singapore-postgres.render.com:5432/decision_assistant_0981"
$env:DEEPSEEK_API_KEY = "YOUR_DEEPSEEK_KEY"
$env:USE_DATABASE = "true"
$env:ENABLE_USER_PROFILING = "true"

Write-Host "⚠️ 请先编辑 test_with_env.ps1 文件，填入:" -ForegroundColor Yellow
Write-Host "   1. DATABASE_URL 中的密码（替换 YOUR_PASSWORD）" -ForegroundColor Yellow
Write-Host "   2. DEEPSEEK_API_KEY（替换 YOUR_DEEPSEEK_KEY）" -ForegroundColor Yellow
Write-Host ""
Write-Host "按任意键继续测试..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
Write-Host ""

# 测试1: 创建数据库表
Write-Host "1. 创建数据库表..." -ForegroundColor Green
python create_user_profile_tables.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "   ❌ 失败" -ForegroundColor Red
    exit 1
}
Write-Host ""

# 测试2: 运行系统测试
Write-Host "2. 运行系统测试..." -ForegroundColor Green
python test_profile_system.py
Write-Host ""

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "测试完成" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "如果测试通过，可以继续:" -ForegroundColor Green
Write-Host "  1. 分析用户: python scheduled_profile_analysis.py --user <username>" -ForegroundColor White
Write-Host "  2. 查看文档: cat USER_PROFILE_SYSTEM_GUIDE.md" -ForegroundColor White
Write-Host ""

