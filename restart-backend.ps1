# 重启后端服务器
Write-Host "🔄 重启后端服务器..." -ForegroundColor Yellow
Write-Host ""

# 设置环境变量
$env:ALPHA_VANTAGE_KEY="QKO2M2K3LZ58ACO2"
$env:DEEPSEEK_API_KEY="sk-d3196d8e68c44690998d79c715ce715d"

# 进入backend目录并启动
Set-Location backend
Write-Host "✅ 环境变量已设置" -ForegroundColor Green
Write-Host "🚀 启动Flask服务器..." -ForegroundColor Cyan
Write-Host ""

python app.py

