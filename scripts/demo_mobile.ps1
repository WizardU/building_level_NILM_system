# One-command Mobile (H5) demo for Windows PowerShell
$ErrorActionPreference = "Stop"
$ROOT = Split-Path -Parent $PSScriptRoot
Set-Location $ROOT

$ML_PY = "$ROOT\ml\.venv\Scripts\python.exe"
$BE_PY = "$ROOT\backend\.venv\Scripts\python.exe"
$BE_UVICORN = "$ROOT\backend\.venv\Scripts\uvicorn.exe"
$NPM = "npm"

function Wait-ForUrl($url, $label, $max = 30) {
    Write-Host -NoNewline "Waiting for $label ($url) "
    for ($i = 0; $i -lt $max; $i++) {
        try {
            $r = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 1 -ErrorAction Stop
            if ($r.StatusCode -eq 200) {
                Write-Host " OK"
                return
            }
        } catch {}
        Write-Host -NoNewline "."
        Start-Sleep -Seconds 1
    }
    Write-Host " FAILED"
    exit 1
}

Write-Host "==> Ensure synthetic data + models"
if (-not (Test-Path "$ROOT\ml\.venv")) {
    Set-Location "$ROOT\ml"; python -m venv .venv
}
& $ML_PY -m pip install -q -r "$ROOT\ml\requirements.txt"
if (-not (Test-Path "$ROOT\data\processed\dataset_manifest.json")) {
    & $ML_PY -m preprocess.generate_synthetic --days 2
}
if (-not (Test-Path "$ROOT\ml\checkpoints\fridge_attention.onnx")) {
    & $ML_PY -m train.train_all --epochs 2 --models baseline attention
    & $ML_PY -m export.export_onnx --all
}

Write-Host "==> Start backend (SQLite) on http://127.0.0.1:8000"
if (-not (Test-Path "$ROOT\backend\.venv")) {
    Set-Location "$ROOT\backend"; python -m venv .venv
}
& $BE_PY -m pip install -q -r "$ROOT\backend\requirements.txt"

$backend = Start-Process -FilePath $BE_UVICORN -ArgumentList "app.main:app","--host","0.0.0.0","--port","8000","--log-level","warning" -WorkingDirectory "$ROOT\backend" -RedirectStandardOutput "$ROOT\backend\demo.log" -RedirectStandardError "$ROOT\backend\demo.err.log" -WindowStyle Hidden -PassThru

Wait-ForUrl "http://127.0.0.1:8000/health" "backend"

Write-Host "==> Start replay adapter"
$replay = Start-Process -FilePath $BE_PY -ArgumentList "-m","adapters.replay.cli","--meter-id","101","--speed","20" -WorkingDirectory "$ROOT\backend" -WindowStyle Hidden -PassThru

Start-Sleep -Seconds 2

Write-Host "==> Install mobile dependencies (if needed)"
Set-Location "$ROOT\mobile"
if (-not (Test-Path "node_modules")) {
    & $NPM install
}

Write-Host "==> Start mobile H5 dev server"
$mobile = Start-Process -FilePath $NPM -ArgumentList "run","dev:h5" -WorkingDirectory "$ROOT\mobile" -RedirectStandardOutput "$ROOT\mobile\demo.log" -RedirectStandardError "$ROOT\mobile\demo.err.log" -WindowStyle Hidden -PassThru

Start-Sleep -Seconds 5

$ip = (Get-NetIPAddress -AddressFamily IPv4 -PrefixOrigin Dhcp | Select-Object -First 1).IPAddress
if (-not $ip) { $ip = "127.0.0.1" }

Write-Host ""
Write-Host "================================================"
Write-Host " Mobile demo is running!"
Write-Host "   Mobile: http://$ip`:3100"
Write-Host "   Local:  http://127.0.0.1:3100"
Write-Host "   API:    http://127.0.0.1:8000"
Write-Host "   Login:  admin / admin123"
Write-Host "   Logs:   backend\demo.log, backend\replay.log, mobile\demo.log"
Write-Host "================================================"
Write-Host "Press Enter to stop all demo processes."
Read-Host

Write-Host ""
Write-Host "==> Stopping demo processes..."
Stop-Process -Id $mobile.Id -ErrorAction SilentlyContinue
Stop-Process -Id $replay.Id -ErrorAction SilentlyContinue
Stop-Process -Id $backend.Id -ErrorAction SilentlyContinue
