# One-command Web demo on Windows (real UK-DALE data + ONNX models).
#
#   .\scripts\demo_web.ps1                 # use existing data/models
#   .\scripts\demo_web.ps1 -Download       # download UK-DALE (~5.1 GB) if missing
#   .\scripts\demo_web.ps1 -Retrain        # retrain attention + baseline, re-export ONNX
#   .\scripts\demo_web.ps1 -ResetDb        # recreate the SQLite database
param(
    [switch]$Download,
    [switch]$Retrain,
    [switch]$ResetDb
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

$MlPython = "$Root\ml\.venv\Scripts\python.exe"
$BePython = "$Root\backend\.venv\Scripts\python.exe"
$Uvicorn = "$Root\backend\.venv\Scripts\uvicorn.exe"
$H5 = "$Root\data\raw\ukdale.h5"
$Manifest = "$Root\data\processed\dataset_manifest.json"

function Ensure-Venv($dir, $python) {
    if (-not (Test-Path $python)) {
        Write-Host "==> Creating venv: $dir"
        python -m venv $dir
    }
}

function Has-RealManifest {
    if (-not (Test-Path $Manifest)) { return $false }
    try {
        $m = Get-Content $Manifest -Raw | ConvertFrom-Json
        return $m.dataset -like "ukdale*"
    } catch { return $false }
}

Ensure-Venv "$Root\ml\.venv" $MlPython
Ensure-Venv "$Root\backend\.venv" $BePython

& $MlPython -c "import torch, h5py, hdf5plugin, pandas" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "==> Install ML dependencies"
    & $MlPython -m pip install -q -r "$Root\ml\requirements.txt"
}
& $BePython -c "import fastapi, onnxruntime, sqlalchemy" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "==> Install backend dependencies"
    & $BePython -m pip install -q -r "$Root\backend\requirements.txt"
}

if (-not (Test-Path $H5)) {
    if (-not $Download) {
        Write-Host "UK-DALE HDF5 not found: $H5"
        Write-Host "Run once with:  .\scripts\demo_web.ps1 -Download"
        exit 1
    }
    Write-Host "==> Download UK-DALE (5.1 GB, resumable)"
    & $MlPython "$Root\scripts\download_datasets.py" --dataset ukdale
    & $MlPython "$Root\scripts\extract_ukdale.py"
}

if (-not (Test-Path "$Root\data\raw\whited")) {
    Write-Host "==> WHITED is optional (appliance transients); skipping. Download with:"
    Write-Host "    $MlPython scripts/download_datasets.py --dataset whited"
}

if ((-not (Has-RealManifest)) -or $Retrain) {
    Write-Host "==> Build UK-DALE house 1 windows (6 s, W=599)"
    Push-Location "$Root\ml"
    & $MlPython -m preprocess.ukdale --h5 "..\data\raw\ukdale.h5" --house 1
    Pop-Location
}

if ($Retrain -or -not (Get-ChildItem "$Root\ml\checkpoints\*_attention.onnx" -ErrorAction SilentlyContinue)) {
    Write-Host "==> Train attention + baseline and export ONNX (GPU when available)"
    $device = & $MlPython -c "import torch; print('cuda' if torch.cuda.is_available() else 'cpu')"
    Push-Location "$Root\ml"
    & $MlPython -u -m train.train_all --models attention baseline --epochs 3 --device $device
    & $MlPython -m export.export_onnx --all
    & $MlPython -m eval.export_thesis_tables
    Pop-Location
}

if ($ResetDb) {
    Write-Host "==> Reset SQLite database"
    Remove-Item "$Root\backend\nilm.db" -Force -ErrorAction SilentlyContinue
}

Write-Host "==> Start backend on http://127.0.0.1:8000"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$Root\backend'; & '$BePython' -m uvicorn app.main:app --host 127.0.0.1 --port 8000"

for ($i = 0; $i -lt 40; $i++) {
    try {
        $ready = Invoke-RestMethod -Uri "http://127.0.0.1:8000/readyz" -TimeoutSec 2
        if ($ready.models_ready) { break }
    } catch {}
    Start-Sleep -Seconds 1
}

Write-Host "==> Start replay adapter (real UK-DALE day, 20 samples/s)"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$Root'; & '$BePython' -m adapters.replay.cli --meter-id 101 --speed 20"

Write-Host "==> Start Vue web console on http://localhost:3000"
if (-not (Test-Path "$Root\web\node_modules")) {
    Push-Location "$Root\web"; npm install; Pop-Location
}
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$Root\web'; npm run dev"

Write-Host ""
Write-Host "================================================"
Write-Host " Web:     http://localhost:3000"
Write-Host " API:     http://127.0.0.1:8000/docs"
Write-Host " Health:  http://127.0.0.1:8000/readyz"
Write-Host " Login:   admin / admin123"
Write-Host " Data:    UK-DALE house 1 (6 s, 5 appliances)"
Write-Host "================================================"
