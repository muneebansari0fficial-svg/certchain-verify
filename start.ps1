# ============================================
# CertChain Verify - Silent Start
# ============================================

Clear-Host

Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "    CertChain Verify - Starting..." -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Logs folder banao
$logDir = "$PWD\logs"
if (-not (Test-Path $logDir)) {
    New-Item -ItemType Directory -Path $logDir | Out-Null
}

# --------------------------------------------
# Step 0: Purane processes clean karo
# --------------------------------------------

Write-Host "[0/5] Cleaning old processes..." -ForegroundColor Yellow

Get-Process node -ErrorAction SilentlyContinue | Stop-Process -Force
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force

Start-Sleep -Seconds 3

Write-Host "      Done." -ForegroundColor Gray

# --------------------------------------------
# Step 1: Hardhat Node (hidden window)
# --------------------------------------------

Write-Host ""
Write-Host "[1/5] Starting Hardhat Node..." -ForegroundColor Yellow

Start-Process powershell `
    -ArgumentList "-WindowStyle", "Hidden", "-Command", "cd '$PWD'; npx hardhat node *> '$logDir\hardhat.log'" `
    -WindowStyle Hidden

Write-Host "      Waiting 12 seconds..." -ForegroundColor Gray

Start-Sleep -Seconds 12

# --------------------------------------------
# Step 2: Deploy Contract
# --------------------------------------------

Write-Host ""
Write-Host "[2/5] Deploying CertificateRegistry..." -ForegroundColor Yellow

$deployOutput = npx hardhat run scripts/deploy.ts --network localhost 2>&1

$deployOutput | ForEach-Object { Write-Host "      $_" -ForegroundColor Gray }

# Address extract karo
$addressLine = $deployOutput | Select-String "0x[a-fA-F0-9]{40}"

if ($addressLine) {

    $newAddress = $addressLine.Matches[0].Value

    Write-Host ""
    Write-Host "      Contract Address: $newAddress" -ForegroundColor Green

    # .env update karo
    $envPath = "$PWD\backend\.env"

    if (Test-Path $envPath) {

        $envContent = Get-Content $envPath -Raw
        $envContent = $envContent -replace "CONTRACT_ADDRESS=0x[a-fA-F0-9]{40}", "CONTRACT_ADDRESS=$newAddress"
        Set-Content $envPath -Value $envContent -NoNewline

        Write-Host "      backend/.env updated!" -ForegroundColor Green

    } else {

        Write-Host "      WARNING: backend/.env not found!" -ForegroundColor Red

    }

} else {

    Write-Host "      ERROR: Could not extract address!" -ForegroundColor Red

}

# --------------------------------------------
# Step 3: Register Institution
# --------------------------------------------

Write-Host ""
Write-Host "[3/5] Registering ABC University..." -ForegroundColor Yellow

npx hardhat run scripts/registerInstitution.ts --network localhost 2>&1 | ForEach-Object { Write-Host "      $_" -ForegroundColor Gray }

# --------------------------------------------
# Step 4: Backend (hidden)
# --------------------------------------------

Write-Host ""
Write-Host "[4/5] Starting FastAPI Backend..." -ForegroundColor Yellow

Start-Process powershell `
    -ArgumentList "-WindowStyle", "Hidden", "-Command", "cd '$PWD'; python -m uvicorn backend.main:app --reload *> '$logDir\backend.log'" `
    -WindowStyle Hidden

Start-Sleep -Seconds 4

# --------------------------------------------
# Step 5: Frontend (hidden)
# --------------------------------------------

Write-Host ""
Write-Host "[5/5] Starting React Frontend..." -ForegroundColor Yellow

Start-Process powershell `
    -ArgumentList "-WindowStyle", "Hidden", "-Command", "cd '$PWD\frontend'; npm run dev *> '$logDir\frontend.log'" `
    -WindowStyle Hidden

Start-Sleep -Seconds 5

# --------------------------------------------
# Done
# --------------------------------------------

Write-Host ""
Write-Host "=========================================" -ForegroundColor Green
Write-Host "      All Services Started!" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Frontend:   http://localhost:5173" -ForegroundColor Cyan
Write-Host "Backend:    http://127.0.0.1:8000" -ForegroundColor Cyan
Write-Host "Blockchain: http://127.0.0.1:8545" -ForegroundColor Cyan
Write-Host ""
Write-Host "Logs:" -ForegroundColor Yellow
Write-Host "  $logDir\hardhat.log" -ForegroundColor Gray
Write-Host "  $logDir\backend.log" -ForegroundColor Gray
Write-Host "  $logDir\frontend.log" -ForegroundColor Gray
Write-Host ""
Write-Host "To STOP all services, run: .\stop.ps1" -ForegroundColor Magenta
Write-Host ""
Write-Host "Press any key to close this window..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")