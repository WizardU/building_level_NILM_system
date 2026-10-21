@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion

set "ROOT=%~dp0.."
cd /d "%ROOT%"

set "ML_PY=%ROOT%\ml\.venv\Scripts\python.exe"
set "BE_PY=%ROOT%\backend\.venv\Scripts\python.exe"
set "BE_UVICORN=%ROOT%\backend\.venv\Scripts\uvicorn.exe"
set "NPM=npm"

echo ==^> Ensure synthetic data + models
if not exist "%ROOT%\ml\.venv" (
  cd /d "%ROOT%\ml" && python -m venv .venv
)
"%ML_PY%" -m pip install -q -r "%ROOT%\ml\requirements.txt"
if not exist "%ROOT%\data\processed\dataset_manifest.json" (
  "%ML_PY%" -m preprocess.generate_synthetic --days 2
)
if not exist "%ROOT%\ml\checkpoints\fridge_attention.onnx" (
  "%ML_PY%" -m train.train_all --epochs 2 --models baseline attention
  "%ML_PY%" -m export.export_onnx --all
)

echo ==^> Start backend (SQLite) on http://127.0.0.1:8000
if not exist "%ROOT%\backend\.venv" (
  cd /d "%ROOT%\backend" && python -m venv .venv
)
"%BE_PY%" -m pip install -q -r "%ROOT%\backend\requirements.txt"

cd /d "%ROOT%\backend"
start "NILM Backend" cmd /c "%BE_UVICORN% app.main:app --host 0.0.0.0 --port 8000 --log-level warning ^>^"%ROOT%\backend\demo.log^" 2^>^&1"

:wait_backend
timeout /t 1 /nobreak >nul
curl -s http://127.0.0.1:8000/health >nul 2>&1
if errorlevel 1 goto wait_backend
echo Backend OK

echo ==^> Start replay adapter
start "NILM Replay" cmd /c "%BE_PY%" -m adapters.replay.cli --meter-id 101 --speed 20

echo ==^> Install mobile dependencies (if needed)
cd /d "%ROOT%\mobile"
if not exist "node_modules" (
  "%NPM%" install
)

echo ==^> Start mobile H5 dev server
start "NILM Mobile" cmd /c "%NPM%" run dev:h5 ^>^"%ROOT%\mobile\demo.log^" 2^>^&1

timeout /t 5 /nobreak >nul

for /f "tokens=1 delims=" %%a in ('powershell -Command "(Get-NetIPAddress -AddressFamily IPv4 -PrefixOrigin Dhcp).IPAddress"') do set "HOST_IP=%%a"
if "!HOST_IP!"=="" set "HOST_IP=127.0.0.1"

echo.
echo ========================================================
echo Mobile demo is running!
echo   Mobile: http://!HOST_IP!:3100
echo   Local:  http://127.0.0.1:3100
echo   API:    http://127.0.0.1:8000
echo   Login:  admin / admin123
echo   Logs:   backend\demo.log, backend\replay.log, mobile\demo.log
echo ========================================================
echo Close the opened command windows to stop all processes.
pause
