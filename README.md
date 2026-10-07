# Building-Level NILM System

Non-Intrusive Load Monitoring for buildings: Seq2Point disaggregation, FastAPI backend ([openapi/NILM.json](openapi/NILM.json)), Vue Web console, Uni-app mobile client, and meter adapters (UK-DALE replay + optional Modbus/MQTT).

## Quick start (Web demo)

```bash
# 1) Generate synthetic training windows + train baseline models (no UK-DALE required)
cd ml
python -m venv .venv
# Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m preprocess.generate_synthetic
python -m train.train_all --epochs 3
python -m export.export_onnx

# 2) Backend + DB
cd ../backend
pip install -r requirements.txt
# Optional: docker compose up -d db
# Or use SQLite (default when DATABASE_URL unset)
uvicorn app.main:app --reload --port 8000

# 3) Web
cd ../web
npm install
npm run dev
```

Open http://localhost:3000 — login `admin` / `admin123`.

One-command local demo (PowerShell or Bash):

```powershell
# Windows PowerShell
.\scripts\demo_web.ps1

# Git Bash / WSL / Linux / macOS
bash scripts/demo_web.sh
```

One-command Docker demo (after models exist under `ml/checkpoints/`):

```bash
docker compose up --build
```

## Layout

| Path | Role |
|------|------|
| `openapi/` | OpenAPI contract |
| `ml/` | Preprocess, Seq2Point train/eval, ONNX export/inference |
| `backend/` | FastAPI + JWT + disaggregation jobs |
| `web/` | Vue 3 + Element Plus + ECharts console |
| `mobile/` | Uni-app basic client (not in demo path) |
| `adapters/` | Replay simulator + Modbus/MQTT sources |
| `data/` | Raw / processed datasets |

## Demo script

1. Start backend (seeds Building A / Floor 1 / Meter 101).
2. `python -m adapters.replay.cli --meter-id 101 --speed 20`
3. Open Dashboard → live mains + appliance stack; Evaluation → metrics; Analytics → energy share.
