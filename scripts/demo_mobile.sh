#!/usr/bin/env bash
# One-command Mobile (H5) demo for Git Bash / WSL / Linux / macOS
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" || "$OSTYPE" == "win32" ]]; then
  ML_PY="$ROOT/ml/.venv/Scripts/python"
  BE_PY="$ROOT/backend/.venv/Scripts/python"
  BE_UVICORN="$ROOT/backend/.venv/Scripts/uvicorn"
  NPM="npm"
else
  ML_PY="$ROOT/ml/.venv/bin/python"
  BE_PY="$ROOT/backend/.venv/bin/python"
  BE_UVICORN="$ROOT/backend/.venv/bin/uvicorn"
  NPM="npm"
fi

wait_for_url() {
  local url=$1 label=$2 max=${3:-30}
  echo -n "Waiting for $label ($url) "
  for ((i=0; i<max; i++)); do
    if curl -s "$url" >/dev/null 2>&1; then
      echo " OK"
      return 0
    fi
    echo -n "."
    sleep 1
  done
  echo " FAILED"
  return 1
}

echo "==> Check real data and ONNX models"
if [[ ! -f "$ROOT/data/raw/ukdale.h5" || ! -f "$ROOT/data/processed/dataset_manifest.json" ]]; then
  echo "Missing UK-DALE data. Run scripts/download_datasets.py and preprocess.ukdale first (see DEMO.md)."
  exit 1
fi
if ! ls "$ROOT/ml/checkpoints/"*_attention.onnx >/dev/null 2>&1; then
  echo "Missing ONNX models. Run train_all + export_onnx first (see DEMO.md)."
  exit 1
fi
NODE_MAJOR=$(node -p "process.versions.node.split('.')[0]" 2>/dev/null || echo 0)
if [[ "$NODE_MAJOR" -lt 22 ]]; then
  echo "Node >= 22.12 is required by uni-app (current: $(node --version 2>/dev/null || echo none))."
  exit 1
fi

echo "==> Start backend (SQLite) on http://127.0.0.1:8000"
(
  cd "$ROOT/backend"
  if [[ ! -d .venv ]]; then python -m venv .venv; fi
  if ! "$BE_PY" -c "import fastapi, onnxruntime, sqlalchemy" >/dev/null 2>&1; then
    "$BE_PY" -m pip install -q -r requirements.txt
  fi
)
cd "$ROOT/backend"
nohup "$BE_UVICORN" app.main:app --host 0.0.0.0 --port 8000 --log-level warning > "$ROOT/backend/demo.log" 2>&1 &
BACKEND_PID=$!
cd "$ROOT"
wait_for_url http://127.0.0.1:8000/health backend

echo "==> Start replay adapter"
nohup "$BE_PY" -m adapters.replay.cli --meter-id 101 --speed 20 > "$ROOT/backend/replay.log" 2>&1 &
REPLAY_PID=$!
sleep 2

echo "==> Install mobile dependencies (if needed)"
(
  cd "$ROOT/mobile"
  if [[ ! -d node_modules ]]; then "$NPM" install; fi
)

echo "==> Start mobile H5 dev server"
cd "$ROOT/mobile"
nohup "$NPM" run dev:h5 > "$ROOT/mobile/demo.log" 2>&1 &
MOBILE_PID=$!
cd "$ROOT"
sleep 5

HOST_IP=$(hostname -I 2>/dev/null | awk '{print $1}' || echo "127.0.0.1")

echo ""
echo "================================================"
echo " Mobile demo is running!"
echo "   Mobile: http://$HOST_IP:3100"
echo "   Local:  http://127.0.0.1:3100"
echo "   API:    http://127.0.0.1:8000"
echo "   Login:  admin / admin123"
echo "   Logs:   backend/demo.log, backend/replay.log, mobile/demo.log"
echo "================================================"
echo "Press Ctrl+C to stop all demo processes."

cleanup() {
  echo ""
  echo "==> Stopping demo processes..."
  kill "$MOBILE_PID" "$REPLAY_PID" "$BACKEND_PID" 2>/dev/null || true
  wait 2>/dev/null || true
  exit 0
}
trap cleanup INT TERM
wait
