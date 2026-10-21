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

## Mobile demo

A Uni-app + Vue 3 mobile client lives in `mobile/`. It shares the same FastAPI backend and supports H5 / WeChat mini-program / Android / iOS builds.

One-command mobile demo (backend + H5 dev server):

```powershell
# Windows PowerShell
.\scripts\demo_mobile.ps1

# Windows CMD
scripts\demo_mobile.cmd

# Git Bash / WSL / Linux / macOS
bash scripts/demo_mobile.sh
```

Or start it manually:

```bash
cd mobile
npm install
npm run dev:h5
```

Open the printed URL (default http://localhost:3100) and log in with `admin` / `admin123`. For physical phone preview, update `mobile/utils/config.js` to use your computer's LAN IP.

See [mobile/README.md](mobile/README.md) for details.

## Layout

| Path | Role |
|------|------|
| `openapi/` | OpenAPI contract |
| `ml/` | Preprocess, Seq2Point train/eval, ONNX export/inference |
| `ml/legacy_nilm/` | Reference Seq2Point/Seq2Seq implementation (from Nilm.rar) |
| `backend/` | FastAPI + JWT + disaggregation jobs |
| `web/` | Vue 3 + Element Plus + ECharts console |
| `mobile/` | Uni-app basic client (not in demo path) |
| `adapters/` | Replay simulator + Modbus/MQTT sources |
| `data/` | Raw / processed datasets |

## Reference NILM implementation

The `ml/legacy_nilm/` directory contains a self-contained reference implementation (originally from `Nilm.rar`) with:

- `Seq2PointCNN` and `Seq2SeqLSTM` models
- Sliding-window training / disaggregation pipeline
- Event-level P/R/F1 evaluation
- CSV-based synthetic data generator
- Streamlit demo app

Useful parts have been integrated into the main system:

- `Seq2SeqLSTM` is available in `ml/models/seq2seq.py` and selectable via `build_model("seq2seq")`
- Event-level F1 metrics are added to `ml/train/metrics.py`
- `ml/preprocess/generate_csv_demo.py` produces UK-DALE-style CSV data

To run the standalone reference demo:

```bash
cd ml/legacy_nilm
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
python make_demo_data.py
python train.py --appliance kettle --model seq2point --epochs 6
python -m streamlit run app.py
```

## Demo script

1. Start backend (seeds Building A / Floor 1 / Meter 101).
2. `python -m adapters.replay.cli --meter-id 101 --speed 20`
3. Open Dashboard → live mains + appliance stack; Evaluation → metrics; Analytics → energy share.

## Using the Nilm.rar legacy reference inside the demo

The FastAPI backend can fall back to the `ml/legacy_nilm` PyTorch checkpoints when no ONNX models exist. To set this up:

```bash
# 1) Train legacy checkpoints
cd ml/legacy_nilm
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
python make_demo_data.py
python train.py --appliance kettle --model seq2point --epochs 6
python train.py --appliance microwave --model seq2point --epochs 6
python train.py --appliance washing_machine --model seq2point --epochs 6
python train.py --appliance fridge --model seq2point --epochs 6

# 2) Import the demo aggregate data into the backend DB
cd ../..
backend/.venv/Scripts/python scripts/import_legacy_data.py

# 3) Start backend (it auto-discovers ml/legacy_nilm/outputs/checkpoints/*.pt)
cd backend
.venv\Scripts\uvicorn app.main:app --reload --port 8000
```

Notes:

- `backend/requirements.txt` includes `pandas`; `torch` is optional and only needed when you want the backend to serve legacy `.pt` checkpoints directly.
- If `torch` is not installed in the backend venv, the legacy fallback is skipped and the heuristic fallback is used instead.
