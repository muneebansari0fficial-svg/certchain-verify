Write-Host ""
Write-Host "Stopping CertChain Verify services..." -ForegroundColor Yellow

Get-Process node -ErrorAction SilentlyContinue | Stop-Process -Force
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force

Start-Sleep -Seconds 2

Write-Host "All services stopped." -ForegroundColor Green
Write-Host ""