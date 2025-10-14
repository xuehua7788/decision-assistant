# 用户和聊天记录查看器
# PowerShell 脚本

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Decision Assistant 数据查看器" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. 查看用户数据
if (Test-Path "backend\users_data.json") {
    Write-Host "📊 注册用户:" -ForegroundColor Green
    Write-Host ""
    
    $users = Get-Content backend\users_data.json | ConvertFrom-Json
    $userCount = 0
    
    foreach ($prop in $users.PSObject.Properties) {
        $userCount++
        $username = $prop.Name
        $userData = $prop.Value
        
        Write-Host "  👤 用户 $userCount : $username" -ForegroundColor Yellow
        $status = if ($userData.is_active) { "✅ 活跃" } else { "❌ 禁用" }
        Write-Host "     状态: $status" -ForegroundColor White
        Write-Host ""
    }
    
    Write-Host "  总用户数: $userCount" -ForegroundColor Cyan
    Write-Host ""
} else {
    Write-Host "❌ 用户数据文件不存在" -ForegroundColor Red
    Write-Host ""
}

# 2. 查看聊天记录文件
Write-Host "----------------------------------------" -ForegroundColor Cyan
Write-Host "💬 聊天记录文件:" -ForegroundColor Green
Write-Host ""

$chatPath = "backend\chat_data"
if (Test-Path $chatPath) {
    $chatFiles = Get-ChildItem "$chatPath\*.json" -ErrorAction SilentlyContinue
    
    if ($chatFiles.Count -gt 0) {
        foreach ($file in $chatFiles) {
            $fileSize = [math]::Round($file.Length / 1KB, 2)
            Write-Host "  📁 $($file.Name)" -ForegroundColor Yellow
            Write-Host "     大小: $fileSize KB" -ForegroundColor White
            Write-Host "     修改: $($file.LastWriteTime)" -ForegroundColor White
            Write-Host ""
        }
        Write-Host "  聊天记录文件数: $($chatFiles.Count)" -ForegroundColor Cyan
    } else {
        Write-Host "  ⚠️  暂无聊天记录" -ForegroundColor Yellow
    }
} else {
    Write-Host "  ⚠️  聊天记录目录不存在" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 询问是否查看详细信息
$choice = Read-Host "是否查看某个用户的详细信息？(输入用户名，或按Enter跳过)"

if ($choice -ne "") {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "  用户详情: $choice" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    
    $users = Get-Content backend\users_data.json | ConvertFrom-Json
    
    if ($users.$choice) {
        Write-Host "✅ 用户信息:" -ForegroundColor Green
        Write-Host "   用户名: $choice" -ForegroundColor Yellow
        Write-Host "   活跃状态: $($users.$choice.is_active)" -ForegroundColor Yellow
        Write-Host "   密码哈希: $($users.$choice.hashed_password.Substring(0,30))..." -ForegroundColor Gray
        Write-Host ""
        
        # 检查是否有聊天记录
        $chatFile = "backend\chat_data\$choice.json"
        if (Test-Path $chatFile) {
            Write-Host "💬 后端聊天记录:" -ForegroundColor Green
            Write-Host ""
            $messages = Get-Content $chatFile | ConvertFrom-Json
            
            if ($messages.messages) {
                $messages.messages | ForEach-Object {
                    if ($_.role -eq "user") {
                        Write-Host "  👤 用户: $($_.content)" -ForegroundColor Cyan
                    } else {
                        Write-Host "  🤖 助手: $($_.content)" -ForegroundColor Yellow
                    }
                    Write-Host ""
                }
            } else {
                Write-Host "  暂无消息记录" -ForegroundColor Gray
            }
        } else {
            Write-Host "  ⚠️  该用户暂无后端聊天记录" -ForegroundColor Yellow
            Write-Host "  (前端聊天记录存储在浏览器 localStorage 中)" -ForegroundColor Gray
        }
    } else {
        Write-Host "❌ 用户不存在: $choice" -ForegroundColor Red
    }
    
    Write-Host ""
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

