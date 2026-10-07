# One-command-ish Web demo (PowerShell)
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

Write-Host "==> Ensure synthetic data + models"
Push-Location "$Root\ml"
if (-not (Test-Path ".\.venv")) { python -m venv .venv }
.\.venv\Scripts\Activate.ps1
pip install -q -r requirements.txt
if (-not (Test-Path "..\data\processed\dataset_manifest.json")) {
  python -m preprocess.generate_synthetic --days 2
}
if (-not (Get-ChildItem checkpoints\*.pt -ErrorAction SilentlyContinue)) {
  python -m train.train_all --epochs 2 --models baseline attention
  python -m export.export_onnx --all
}
python -m eval.export_thesis_tables
Pop-Location

Write-Host "==> Start backend (SQLite)"
Push-Location "$Root\backend"
if (-not (Test-Path ".\.venv")) { python -m venv .venv }
.\.venv\Scripts\Activate.ps1
pip install -q -r requirements.txt
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$Root\backend'; .\.venv\Scripts\Activate.ps1; uvicorn app.main:app --reload --port 8000"
Pop-Location

Start-Sleep -Seconds 3
Write-Host "==> Start replay adapter"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$Root'; .\backend\.venv\Scripts\Activate.ps1; python -m adapters.replay.cli --meter-id 101 --speed 20"

Write-Host "==> Start web"
Push-Location "$Root\web"
if (-not (Test-Path "node_modules")) { npm install }
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$Root\web'; npm run dev"
Pop-Location

Write-Host "Open http://localhost:3000  login admin / admin123"
