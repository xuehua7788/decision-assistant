# Decision Assistant 数据查看器

Write-Host "`n========================================"
Write-Host "  Decision Assistant 数据查看器"
Write-Host "========================================`n"

# 查看用户数据
if (Test-Path "backend\users_data.json") {
    Write-Host "注册用户:" -ForegroundColor Green
    Write-Host ""
    
    $users = Get-Content backend\users_data.json | ConvertFrom-Json
    $userCount = 0
    
    $users.PSObject.Properties | ForEach-Object {
        $userCount++
        Write-Host "  用户 $userCount : $($_.Name)" -ForegroundColor Yellow
        Write-Host "     状态: $($_.Value.is_active)" -ForegroundColor White
        Write-Host ""
    }
    
    Write-Host "  总用户数: $userCount`n" -ForegroundColor Cyan
}

# 查看聊天记录
Write-Host "----------------------------------------"
Write-Host "聊天记录文件:" -ForegroundColor Green
Write-Host ""

if (Test-Path "backend\chat_data") {
    $chatFiles = Get-ChildItem "backend\chat_data\*.json" -ErrorAction SilentlyContinue
    
    if ($chatFiles) {
        $chatFiles | ForEach-Object {
            $size = [math]::Round($_.Length / 1KB, 2)
            Write-Host "  $($_.Name) - ${size}KB - $($_.LastWriteTime)" -ForegroundColor Yellow
        }
        Write-Host "`n  总文件数: $($chatFiles.Count)" -ForegroundColor Cyan
    } else {
        Write-Host "  暂无聊天记录" -ForegroundColor Yellow
    }
}

Write-Host "`n========================================`n"

