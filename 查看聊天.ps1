# 简单的聊天查看器
Write-Host "`n========== 聊天记录查看器 ==========" -ForegroundColor Cyan

# 显示所有聊天文件
Write-Host "`n所有聊天会话：" -ForegroundColor Yellow
$files = Get-ChildItem -Path "chat_data" *.json | Sort-Object LastWriteTime -Descending
$i = 1
foreach ($file in $files) {
    Write-Host "$i. $($file.Name.Substring(0,8))... - $($file.LastWriteTime.ToString('MM/dd HH:mm'))"
    $i++
}

# 让用户选择
Write-Host "`n输入编号查看对应聊天 (直接回车看最新的):" -ForegroundColor Green
$choice = Read-Host

if ($choice -eq "") {
    $selectedFile = $files[0]
} else {
    $selectedFile = $files[$choice - 1]
}

# 显示选中的聊天
Write-Host "`n========== 聊天内容 ==========" -ForegroundColor Cyan
Write-Host "会话: $($selectedFile.Name)" -ForegroundColor Yellow

$content = Get-Content $selectedFile.FullName | ConvertFrom-Json

foreach ($msg in $content.messages) {
    Write-Host "`n" -NoNewline
    if ($msg.role -eq "user") {
        Write-Host "[用户]:" -ForegroundColor Blue
    } else {
        Write-Host "[AI]:" -ForegroundColor Green
    }
    
    # 显示消息（限制长度）
    $text = $msg.content
    if ($text.Length -gt 500) {
        Write-Host $text.Substring(0, 500) 
        Write-Host "...(内容过长，已截断)" -ForegroundColor Gray
    } else {
        Write-Host $text
    }
    Write-Host "---" -ForegroundColor DarkGray
}

Write-Host "`n总消息数: $($content.messages.Count)" -ForegroundColor Yellow
