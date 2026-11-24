# Evidence index

**Branch:** `handoff/usp-engineering-midterm`  
**Tag:** `handoff-usp-2026-11-25`  
**Local commit:** run `git rev-parse --short HEAD` on the branch (the hash is also reported in the handoff message).  
**Base:** `ce8c55c` (main, 2026-11-25), tag `review-response-2026-11-25`  
**Course repo:** `MUST-BIT-BEIE-FYP-2026/fyp-2026-042` — not configured as a git remote in this workspace.

## 1. Engineering evidence (USP)

| # | Evidence | Command / path | Expected |
|---|---|---|---|
| E1 | Backend health + ONNX model version | `curl http://127.0.0.1:8000/readyz` | `backend=onnx`, `models_ready=true` |
| E2 | 21 API checks | `ml/.venv/Scripts/python.exe scripts/smoke_api.py` | `all checks passed` |
| E3 | API contract | `openapi/NILM.json`; `scripts/export_openapi.py` | 38 paths |
| E4 | Dashboard screenshot | `report_build/shots/web_dashboard_tall.png` | current model version, 79.7% Event F1 |
| E5 | Mobile Analytics screenshot | `report_build/shots/mobile_analytics.png` | English UI, cost/energy/alert |
| E6 | Mobile H5 run | `cd mobile && npm run dev:h5` | H5 page loads, 4 tabs |
| E7 | Replay | `python -m adapters.replay.cli --speed 80 --batch 5` | dashboard timestamps advance |

## 2. Midterm ML evidence (USP-owned)

| # | Evidence | Path |
|---|---|---|
| M1 | Midterm 10 ONNX models (5 attention + 5 baseline) | `ml/checkpoints/*.onnx` (gitignored; local restore) |
| M2 | Midterm 3-epoch results / report tables | `FYP-042Progress Report (1).docx` §3–§4 |
| M3 | WHITED RF baseline (44.1% top-1, 18/40 classes) | `ml/checkpoints/whited_metrics.json` |
| M4 | Training/eval code | `ml/models/seq2point.py`, `ml/train/train_one.py`, `ml/eval/evaluate.py` |

## 3. Post-report improvement evidence (handoff to Yang)

| # | Evidence | Path |
|---|---|---|
| A1 | Three-model MSE metrics | `ml/checkpoints/ablation_metrics.json` |
| A2 | Loss ablation 2×2 | `ml/checkpoints/loss_ablation.json` |
| A3 | Cross-house house2 | `ml/checkpoints/cross_house_house2.json` |
| A4 | Block bootstrap CI | `ml/checkpoints/metrics_ci.json` |
| A5 | Microwave 25× | `ml/checkpoints/microwave_wmse25.json` |
| A6 | Written summary | `MODEL_EVIDENCE.md` |
| A7 | Commit/tag | `midterm-2026-11-30-evidence` / `72ed7bf` (main run) |

> These are post-report experiments. The **midterm** report keeps its 3-epoch numbers; these 8-epoch results
> are for Yang's future-improvement track and must not silently replace the midterm table.

## 4. What not to commit

- `data/raw/*.h5`, `data/processed/*` (large, gitignored)
- `ml/checkpoints/*.pt`, `*.onnx`, `*.joblib` (gitignored)
- `.venv/`, `node_modules/`, `.tmp/`, Edge profiles
- Database `backend/nilm.db` (gitignored)
- Any WEMUST/private course file

## 5. Reproduce from a clean checkout

```powershell
# 1. backend venv
cd NILM\backend
python -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt

# 2. model artifacts are local-only; copy from the tagged workspace if available
#    (or let the algorithm owner restore ml/checkpoints/*.onnx)

# 3. start
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000

# 4. checks
cd ..
ml\.venv\Scripts\python.exe scripts\smoke_api.py
```

If the model artifacts are absent, `/readyz` falls back to `heuristic`; do not claim ONNX in that state.

## 6. Report update text (ready to paste)

Replace the `[TBD: USP backend & mobile commits]` row with:

> U SENGPAN — midterm M2 ML training/ONNX/eval + M3 backend + M5 mobile H5:
> branch `handoff/usp-engineering-midterm`, tag `handoff-usp-2026-11-25`,
> commit `<short-hash>` (course repo mirror: `<course-commit>`).
> Evidence: 10 ONNX models, 3-epoch report tables, WHITED RF 44.1%, 21/21 `scripts/smoke_api.py`,
> `report_build/shots/mobile_analytics.png`, `openapi/NILM.json`.

Also change the M2 owner wording (see [REPORT_CORRECTION.md](REPORT_CORRECTION.md)):

> Midterm M2 training/ONNX/WHITED RF: **U SENGPAN**; W5+ M2 improvements: **Yang Yifei**.

Use the actual hash printed after `git push`; do not leave `<...>` in the final report.
