# Evidence index

**Branch:** `handoff/ysb-engineering-midterm`  
**Tag:** `handoff-ysb-2026-11-25`  
**Local commit:** run `git rev-parse --short HEAD` on the branch (the hash is also reported in the handoff message).  
**Base:** `ce8c55c` (main, 2026-11-25), tag `review-response-2026-11-25`  
**Course repo:** `MUST-BIT-BEIE-FYP-2026/fyp-2026-042` — not configured as a git remote in this workspace.

## 1. Engineering evidence (YSB)

| # | Evidence | Command / path | Expected |
|---|---|---|---|
| E1 | Backend health + ONNX model version | `curl http://127.0.0.1:8000/readyz` | `backend=onnx`, `models_ready=true` |
| E2 | 21 API checks | `ml/.venv/Scripts/python.exe scripts/smoke_api.py` | `all checks passed` |
| E3 | API contract | `openapi/NILM.json`; `scripts/export_openapi.py` | 38 paths |
| E4 | Dashboard screenshot | `report_build/shots/web_dashboard_tall.png` | current model version, 79.7% Event F1 |
| E5 | Mobile Analytics screenshot | `report_build/shots/mobile_analytics.png` | English UI, cost/energy/alert |
| E6 | Mobile H5 run | `cd mobile && npm run dev:h5` | H5 page loads, 4 tabs |
| E7 | Replay | `python -m adapters.replay.cli --speed 80 --batch 5` | dashboard timestamps advance |

## 2. Provisional algorithm evidence (to Yang)

| # | Evidence | Path |
|---|---|---|
| A1 | Three-model MSE metrics | `ml/checkpoints/ablation_metrics.json` |
| A2 | Loss ablation 2×2 | `ml/checkpoints/loss_ablation.json` |
| A3 | Cross-house house2 | `ml/checkpoints/cross_house_house2.json` |
| A4 | Block bootstrap CI | `ml/checkpoints/metrics_ci.json` |
| A5 | Microwave 25× | `ml/checkpoints/microwave_wmse25.json` |
| A6 | Written summary | `MODEL_EVIDENCE.md` |
| A7 | Commit/tag | `midterm-2026-11-30-evidence` / `72ed7bf` (main run) |

> These are **provisional**; see `ALGORITHM_PROVISIONAL.md`. They are not YSB's final contribution and
> must not replace the report's 3-epoch numbers without Yang's review.

## 3. What not to commit

- `data/raw/*.h5`, `data/processed/*` (large, gitignored)
- `ml/checkpoints/*.pt`, `*.onnx`, `*.joblib` (gitignored)
- `.venv/`, `node_modules/`, `.tmp/`, Edge profiles
- Database `backend/nilm.db` (gitignored)
- Any WEMUST/private course file

## 4. Reproduce from a clean checkout

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

## 5. Report update text (ready to paste)

Replace the `[TBD: YSB backend & mobile commits]` row with:

> U SENGPAN — backend + mobile H5: branch `handoff/ysb-engineering-midterm`, tag
> `handoff-ysb-2026-11-25`, commit `<short-hash>` (course repo mirror: `<course-commit>`).
> Evidence: 21/21 `scripts/smoke_api.py`, `report_build/shots/mobile_analytics.png`,
> `report_build/shots/web_dashboard_tall.png`, `openapi/NILM.json`.

Use the actual hash printed after `git push`; do not leave `<...>` in the final report.
