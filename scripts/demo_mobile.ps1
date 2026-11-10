# One-command mobile (H5) demo on Windows.
# Uses the bundled Node 22 in .tools when present, because uni-app requires >=22.12.
param(
    [switch]$ResetDb
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

$BePython = "$Root\backend\.venv\Scripts\python.exe"
$BundledNode = "$Root\.tools\node-v22.14.0-win-x64"
$NodeDir = $null
if (Test-Path "$BundledNode\node.exe") {
    $NodeDir = $BundledNode
} else {
    $version = (& node --version) -replace "v", ""
    $major = [int]($version.Split(".")[0])
    if ($major -ge 22) { $NodeDir = (Split-Path (Get-Command node).Source) }
}

if (-not $NodeDir) {
    Write-Host "Node >= 22.12 is required by uni-app."
    Write-Host "Download it with:"
    Write-Host "  $BePython -c ""import urllib.request; urllib.request.urlretrieve('https://nodejs.org/dist/v22.14.0/node-v22.14.0-win-x64.zip', '.tools/node22.zip')"""
    exit 1
}

if (-not (Test-Path $BePython)) {
    Write-Host "Backend venv missing. Run .\scripts\demo_web.ps1 once first."
    exit 1
}

if ($ResetDb) {
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

Write-Host "==> Start replay adapter"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$Root'; & '$BePython' -m adapters.replay.cli --meter-id 101 --speed 20"

Write-Host "==> Start mobile H5 dev server (http://127.0.0.1:3100)"
if (-not (Test-Path "$Root\mobile\node_modules")) {
    Push-Location "$Root\mobile"
    $env:PATH = "$NodeDir;$env:PATH"
    & "$NodeDir\npm.cmd" install --no-audit --no-fund
    Pop-Location
}
Start-Process powershell -ArgumentList "-NoExit", "-Command", "`$env:PATH = '$NodeDir;' + `$env:PATH; Set-Location '$Root\mobile'; & '$NodeDir\npm.cmd' run dev:h5"

Write-Host ""
Write-Host "================================================"
Write-Host " Mobile: http://127.0.0.1:3100"
Write-Host " API:    http://127.0.0.1:8000"
Write-Host " Login:  admin / admin123"
Write-Host "================================================"
