[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
chcp 65001 | Out-Null

Write-Host "========== Chat Viewer ==========" -ForegroundColor Cyan

$files = Get-ChildItem ".\chat_data\*.json" | Sort-Object LastWriteTime -Descending

for ($i=0; $i -lt $files.Count; $i++) {
    Write-Host "$($i+1). $($files[$i].Name)" -ForegroundColor Yellow
}

$choice = Read-Host "Enter number (1-$($files.Count))"
if ($choice) { 
    $files = @($files[$choice-1]) 
}

foreach ($file in $files) {
    Write-Host "`n===== $($file.Name) =====" -ForegroundColor Green
    $content = [System.IO.File]::ReadAllText($file.FullName, [System.Text.Encoding]::UTF8)
    $data = $content | ConvertFrom-Json
    
    foreach ($msg in $data.messages) {
        Write-Host "[$($msg.role)]:" -ForegroundColor Cyan
        Write-Host $msg.content
        Write-Host ""
    }
}

Read-Host "Press Enter to exit"
