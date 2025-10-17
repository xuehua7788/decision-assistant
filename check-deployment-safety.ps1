# ?函蔡???亥???
Write-Host "璉?交?阡?亙甇?＆憿寧..." -ForegroundColor Yellow
$currentProject = vercel project ls | findstr "decision-assistant-frontend-prod"
if ($currentProject) {
    Write-Host "??摰嚗歇?暹??decision-assistant-frontend-prod" -ForegroundColor Green
    return $true
} else {
    Write-Host "???梢嚗?暹?唳迤蝖桅★?殷?" -ForegroundColor Red
    Write-Host "霂瑕?餈?: vercel link --project=decision-assistant-frontend-prod" -ForegroundColor Yellow
    return $false
}
