# Repository map & ownership

**Base:** `ce8c55c` (main), branch `handoff/ysb-engineering-midterm`.

| Path | Owner | Status | Notes |
|---|---|---|---|
| `backend/` | **U SENGPAN** (M3, shared) | working | FastAPI, SQLite, JWT, ONNX serving, replay |
| `mobile/` | **U SENGPAN** (M5, primary) | H5 complete | Uni-app; native iOS/Android deferred |
| `openapi/` | shared contract | working | 38 paths; regenerate with `scripts/export_openapi.py` |
| `scripts/smoke_api.py` | U SENGPAN | working | 21/21 checks |
| `scripts/demo_*` | shared | working | Web/mobile start scripts |
| `adapters/replay/` | shared | working | real replay path |
| `adapters/modbus_mqtt/` | shared | stub | not on the verified path |
| `web/` | Jin Xinyi (M4) | working | Vue 3 console |
| `ml/preprocess/` | Jin Xinyi (M1 official) | mixed | local UK-DALE reader; no REDD/PLAID here |
| `ml/models/`, `ml/train/`, `ml/eval/` | Yang Yifei (M2 official) | provisional local | handoff to Yang; see `ALGORITHM_PROVISIONAL.md` |
| `ml/checkpoints/` | Yang Yifei (after review) | mixed | production ONNX + ablation JSON; `.pt/.onnx` gitignored |
| `data/` | local only | not in git | UK-DALE HDF5 + processed windows |
| `report_build/` | local evidence | not production | scripts, figures, screenshots, logs |
| `HANDOFF/` | **U SENGPAN** | new | this package |
| `archive/legacy_nilm/` | shared | archived | not on runtime path |

## Production vs provisional

**Production path (demo):**
- `backend/` → `mobile/` / `web/`
- `openapi/NILM.json`
- `ml/checkpoints/{appliance}_attention.onnx` + `.json` (5 attention MSE models)
- `ml/checkpoints/{appliance}_baseline.onnx` (5 baseline models for comparison)

**Provisional ablation only (do not present as deployed):**
- `ml/checkpoints/*_mse.pt`, `*_dilated*.pt`, `*_wmse25.pt`
- `ml/checkpoints/ablation_metrics.json`, `loss_ablation.json`, `cross_house_house2.json`, `metrics_ci.json`
- `MODEL_EVIDENCE.md`, `NILM_Review_Response_11.25.pptx`
- These belong to Yang's review; see `ALGORITHM_PROVISIONAL.md`.

## Empty/cleanup notes

- `ml/NILM/` is an empty nested directory; safe to remove.
- `report_build/*.log` and `report_build/.dsh-office-*` are local build artifacts; not required.
- `report_build/progress_report_dump*.txt` are derived from the docx; remove before commit.
