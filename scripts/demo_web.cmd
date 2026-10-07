@echo off
setlocal enabledelayedexpansion

set ROOT=%~dp0..
cd /d %ROOT%

echo ==> Ensure backend deps
cd /d %ROOT%\backend
if not exist .venv (
    python -m venv .venv
)
.venv\Scripts\python -m pip install -q -r requirements.txt
if errorlevel 1 (
    echo Failed to install backend dependencies.
    pause
    exit /b 1
)

echo ==> Start backend
start "NILM Backend" cmd /k "cd /d %ROOT%\backend && .venv\Scripts\uvicorn app.main:app --host 127.0.0.1 --port 8000"

echo ==> Wait for backend ready
:wait
curl -s http://127.0.0.1:8000/health > nul 2>&1
if errorlevel 1 (
    timeout /t 1 > nul
    goto wait
)

echo ==> Start replay adapter
start "NILM Replay" cmd /k "cd /d %ROOT% && backend\.venv\Scripts\python -m adapters.replay.cli --meter-id 101 --speed 20"

echo ==> Start web dev server
cd /d %ROOT%\web
if not exist node_modules (
    npm install
)
start "NILM Web" cmd /k "cd /d %ROOT%\web && npm run dev"

echo.
echo ================================================
echo Demo is running!
echo   Web:    http://localhost:3000
echo   Login:  admin / admin123
echo   API:    http://127.0.0.1:8000
echo ================================================
pause
