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
  (30.7 M params), 8 epochs with MSE on an RTX 3070, exported to ONNX with numerical
  parity checks.
- **Evidence-based metrics**: every number on the Evaluation page comes from
  `ml/checkpoints/ablation_metrics.json` (13,013 test windows per appliance).
- **Second dataset (WHITED)**: 994 start-up transients / 40 appliance labels /
  100 devices, classified with 19 time-frequency features under a **device
  holdout** split (18/40 classes evaluable): accuracy 44.1%, macro F1 27.0%,
  top-3 71.8%. Exposed via `GET /datasets/whited` and the Evaluation page.
- **End-to-end API**: login → buildings/meters → measurements → disaggregation
  → analytics → alerts → dataset cards. `scripts/smoke_api.py` checks the core.
- **Web console**: live mains + per-appliance curves, KPI cards, real model
  metrics, billing/energy breakdown, alert lifecycle.
- **Mobile client**: fully English UI, builds to H5 (uni-app + Node 22).
- **Data quality guardrails**: UTC timestamps, cache keys per time window,
  unique `(meter_id, timestamp)`, alert cooldown, input limits.

## Datasets

| Dataset | Role | Size | License |
|---------|------|------|---------|
| [UK-DALE](https://data.ceda.ac.uk/edc/d1/7d78f943-f9fe-413b-af52-1816f9d968b0) | Disaggregation training/evaluation | 5.47 GB zip → 6.33 GB HDF5 | CC BY 4.0 |
| [WHITED](https://www.cs.cit.tum.de/dis/resources/whited/) | Appliance identification (device-holdout baseline) | 225 MB, 994 FLAC files | CC BY 4.0 |

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
# First run only: downloads 5.47 GB, preprocesses, trains, exports ONNX
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
python -m preprocess.whited --raw ..\data\raw\whited     # WHITED identification baseline
```

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

The backend seeds the demo building and preloads one day of real UK-DALE
samples on first start. `GET /readyz` reports the inference backend
(`onnx` or `heuristic`).

## Results (UK-DALE house 1, test split)

Three-model ablation with the **same MSE loss, 8 epochs and seed 42** (13,013 test windows per appliance):

| Model | MAE | RMSE | State F1 | Event F1 |
|---|---:|---:|---:|---:|
| Baseline CNN | 12.45 W | 62.9 W | 0.790 | 0.789 |
| Dilated only | 12.99 W | 64.1 W | 0.733 | 0.786 |
| Attention (proposed) | **10.45 W** | **62.3 W** | 0.762 | **0.797** |

Honest reading: attention lowers mean MAE by **16.1% vs the MSE baseline**
(proposal target ≥10%: met) and slightly improves Event F1 (0.797 vs 0.789).
Dilation alone does **not** improve the average; baseline still has higher
State F1 (0.790 vs 0.762). Microwave remains weak (Event F1 0.407).

The 2×2 loss ablation (MSE vs weighted Huber) and the house-1 → house-2
cross-house test are in [MODEL_EVIDENCE.md](MODEL_EVIDENCE.md). Key result:
MSE is stronger than weighted Huber at 8 epochs; cross-house Event F1 is
0.775 for attention and 0.814 for baseline, while attention has the lower
cross-house MAE (13.97 vs 15.06 W).

## Layout

| Path | Role |
|------|------|
| `openapi/` | Generated OpenAPI contract (`scripts/export_openapi.py`); `/docs` is live |
| `ml/` | Preprocess, training, evaluation, ONNX export/inference |
| `archive/legacy_nilm/` | Reference implementation from the original Nilm.rar (not on the runtime path) |
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
python scripts/smoke_api.py        # 21 end-to-end API checks
cd web && npm run build            # production build
cd mobile && npm run build:h5      # H5 build (Node >= 22.12)
```

## Known limitations

- Only one house so far; cross-house generalisation is not measured yet.
- No automated unit tests/CI; `smoke_api.py` is the current regression net.
- SQLite + `create_all` (no Alembic migrations yet); Postgres/Timescale is
  wired in Docker Compose but not exercised.
- Mobile H5 is verified by build; device-level WeChat/App builds are untested.
- WHITED is a **strict cross-device baseline**: 22 of 40 classes have a single
  device and are train-only, so only 18 classes are evaluable; a raw-waveform
  CNN is the next step.

## Team

- 金欣怡 — data pipeline, backend, Web console
- 杨一飞 — Seq2Point models, ablations, ONNX
- 余升斌 — mobile client
