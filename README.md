# Building-Level NILM System

Non-Intrusive Load Monitoring for buildings: UK-DALE data pipeline, Seq2Point
disaggregation, FastAPI backend, Vue 3 Web console and a uni-app mobile client.

This repository is no longer a mock-only demo: the Web and mobile clients read
real UK-DALE house 1 data through ONNX Runtime.

## What works today

- **Real dataset**: UK-DALE house 1, 2014-01-01 → 2014-07-01, 2,606,400 samples
  at 6 s resolution, 5 appliances (fridge, kettle, microwave, dishwasher,
  washing machine).
- **Trained models**: Seq2Point attention (9.8 M params) and baseline
  (30.7 M params), 3 epochs on an RTX 3070, exported to ONNX with numerical
  parity checks.
- **Evidence-based metrics**: every number on the Evaluation page comes from
  `ml/checkpoints/ablation_metrics.json` (13,013 test windows per appliance).
- **End-to-end API**: login → buildings/meters → measurements → disaggregation
  → analytics → alerts. `scripts/smoke_api.py` checks all of it.
- **Web console**: live mains + per-appliance curves, KPI cards, real model
  metrics, billing/energy breakdown, alert lifecycle.
- **Mobile client**: fully English UI, builds to H5 (uni-app + Node 22).
- **Data quality guardrails**: UTC timestamps, cache keys per time window,
  unique `(meter_id, timestamp)`, alert cooldown, input limits.

## Datasets

| Dataset | Role | Size | License |
|---------|------|------|---------|
| [UK-DALE](https://data.ceda.ac.uk/edc/d1/7d78f943-f9fe-413b-af52-1816f9d968b0) | Disaggregation training/evaluation | 5.1 GB zip → 5.9 GB HDF5 | CC BY 4.0 |
| [WHITED](https://www.cs.cit.tum.de/dis/resources/whited/) | Appliance transient identification (optional) | 225 MB, 994 FLAC files | CC BY 4.0 |

Download both (resumable):

```bash
python scripts/download_datasets.py --dataset all
python scripts/extract_ukdale.py          # extracts ukdale.h5
```

Files land in `data/raw/` (git-ignored) with a SHA-256 manifest.

> WHITED is transient (high-frequency start-up) data, so it is used for
> appliance identification experiments, not for the 6 s Seq2Point task.

## Quick start (Windows)

```powershell
# First run only: downloads 5.1 GB, preprocesses, trains, exports ONNX
.\scripts\demo_web.ps1 -Download

# Later runs
.\scripts\demo_web.ps1
```

Then open http://localhost:3000 and sign in with `admin` / `admin123`.

Mobile (H5):

```powershell
.\scripts\demo_mobile.ps1
# http://127.0.0.1:3100
```

### Manual pipeline

```bash
cd ml
python -m venv .venv && .venv\Scripts\activate
pip install -r requirements.txt          # includes hdf5plugin (Blosc) and torch

python -m preprocess.ukdale --h5 ..\data\raw\ukdale.h5 --house 1
python -m train.train_all --models attention baseline --epochs 3 --device cuda
python -m export.export_onnx --all
python -m eval.export_thesis_tables
```

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

The backend seeds the demo building and preloads one day of real UK-DALE
samples on first start. `GET /readyz` reports the inference backend
(`onnx` / `torch-legacy` / `heuristic`).

## Results (UK-DALE house 1, test split)

| Appliance | Attention MAE | SAE | State F1 | Event F1 | Baseline MAE | State F1 |
|-----------|--------------:|----:|---------:|---------:|-------------:|---------:|
| fridge | 21.31 W | 0.006 | 0.781 | 0.861 | 20.53 W | 0.784 |
| kettle | 9.21 W | 0.153 | 0.744 | 0.755 | 8.14 W | 0.821 |
| microwave | 6.76 W | 0.345 | 0.152 | 0.288 | 7.08 W | 0.329 |
| dishwasher | 8.72 W | 0.105 | 0.845 | 0.810 | 9.53 W | 0.724 |
| washing machine | 11.15 W | 0.013 | 0.884 | 0.840 | 13.38 W | 0.952 |
| **mean** | — | — | **0.681** | **0.711** | — | **0.722** |

Honest reading: attention wins clearly on dishwasher and washing machine
(especially SAE), but baseline is still better on kettle and microwave, and
slightly better on mean state F1. The current "proposed vs baseline" story is
therefore **not yet a win**; see `IMPROVEMENT_PLAN.md` (threshold search,
positive weighting, longer schedules) and `MIDTERM_STATUS.md`.

## Layout

| Path | Role |
|------|------|
| `openapi/` | Original contract (FastAPI `/docs` is now the source of truth) |
| `ml/` | Preprocess, training, evaluation, ONNX export/inference |
| `ml/legacy_nilm/` | Archived reference implementation (not on the demo path) |
| `backend/` | FastAPI + JWT + disaggregation + analytics |
| `web/` | Vue 3 + Element Plus + ECharts console (bilingual) |
| `mobile/` | uni-app client (English UI, H5/WeChat/App builds) |
| `adapters/` | Replay simulator + optional Modbus/MQTT stubs |
| `data/` | Raw and processed datasets (git-ignored) |
| `scripts/` | Dataset download, extraction, smoke test, demo launchers |

## API

Interactive docs: http://127.0.0.1:8000/docs

Key endpoints (all under `/api/v1` unless noted):

- `POST /auth/login`
- `GET /disaggregation/result?meter_id&start&end&refresh`
- `GET /disaggregation/overview`
- `GET /disaggregation/models`
- `GET /analytics/metrics`, `GET /analytics/reports`
- `GET /analytics/energy`, `GET|PUT /analytics/settings`
- `GET /analytics/alerts`, `POST /analytics/alerts/{id}/resolve`
- `GET /readyz` (root, no auth)

All timestamps are UTC and serialized with a trailing `Z`.

## Tests and checks

```bash
python scripts/smoke_api.py        # 19 end-to-end API checks
cd web && npm run build            # production build
cd mobile && npm run build:h5      # H5 build (Node >= 22.12)
```

## Known limitations

- Only one house so far; cross-house generalisation is not measured yet.
- No automated unit tests/CI; `smoke_api.py` is the current regression net.
- SQLite + `create_all` (no Alembic migrations yet); Postgres/Timescale is
  wired in Docker Compose but not exercised.
- Mobile H5 is verified by build; device-level WeChat/App builds are untested.
- WHITED is downloaded but not yet wired into a UI experiment.

## Team

- 金欣怡 — data pipeline, backend, Web console
- 杨一飞 — Seq2Point models, ablations, ONNX
- 余升斌 — mobile client
