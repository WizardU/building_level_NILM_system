# Algorithm provisional work — handoff to Yang Yifei

> **Status: provisional, frozen, not YSB's final contribution.**
> This folder/file exists because the official M1 preprocessed dataset was not available in YSB's workspace
> during the midterm. It was built only to keep the end-to-end demo and the midterm evidence moving.
> Official ownership per the progress report: **M1 = Jin Xinyi**, **M2 = Yang Yifei**. YSB owns **M3/M5**.

## 1. Why this exists

- YSB did not receive the preprocessing output that M1 (Jin) owns.
- To avoid an empty demo, YSB built a local UK-DALE pipeline and local model/eval scripts.
- Those local numbers **do not replace** the official 3-epoch report numbers and must not be presented
  as Yang's M2 results until Yang reproduces them.

## 2. What was built locally

| Area | Local files | Status |
|---|---|---|
| UK-DALE reader | `ml/preprocess/ukdale.py`, `ml/preprocess/config.py` | custom HDF5 reader (not NILMTK) |
| Windows | `data/processed/*_train/val/test.h5`, `dataset_manifest.json` | local copy, not necessarily M1's official data |
| Models | `ml/models/seq2point.py` (`Seq2Point`, `Seq2PointDilated`, `Seq2PointAttention`) | baseline/dilated/attention |
| Training | `ml/train/train_one.py`, `train_all.py` | 8 epochs, MSE/weighted Huber, val loss, event-F1 checkpoint |
| Evaluation | `ml/eval/evaluate.py` | MAE, RMSE, SAE, state/event F1 |
| Extra experiments | `train_loss_ablation.py`, `train_attention_mse.py`, `train_dilated_mse.py` | 2×2 loss and MSE variants |
| Cross-house | `ml/eval/cross_house.py` | house1 → house2, no retraining |
| CI | `ml/eval/bootstrap_ci.py` | block bootstrap for MAE/RMSE |
| WHITED baseline | `ml/preprocess/whited.py`, `whited_metrics.json` | 19 time-frequency features + Random Forest |

## 3. Results (local, 8-epoch MSE, single seed 42)

| Model | MAE | RMSE | State F1 | Event F1 |
|---|---:|---:|---:|---:|
| Baseline | 12.45 W | 62.9 W | 0.790 | 0.789 |
| Dilated | 12.99 W | 64.1 W | 0.733 | 0.786 |
| Attention | **10.45 W** | **62.3 W** | 0.762 | **0.797** |

- Attention vs MSE baseline: **MAE −16.1%**, Event F1 +0.008, State F1 −0.028.
- Dilated-only does **not** beat baseline; the gain is the attention combination.
- 2×2 loss: MSE beats weighted Huber for both baseline and attention (weighted Huber is not an improvement here).
- Cross-house (house1 → house2, 44,141 windows): attention Event F1 0.775 / MAE 13.97; baseline Event F1 0.814 / MAE 15.06. Ranking flips.
- Microwave: attention MSE Event F1 0.407; 25× positive-weighted MSE → 0.494 (recall 0.68), offline only.
- WHITED: 44.1% top-1 / 27.0% macro F1 / 71.8% top-3; 18/40 classes evaluable, 20 unseen devices.

Full numbers and caveats: `MODEL_EVIDENCE.md`; CI in `ml/checkpoints/metrics_ci.json`.

## 4. Important discrepancies with the progress report

| Report says | Local provisional reality | Action |
|---|---|---|
| 3 epochs; attention 0.71 vs baseline 0.76; microwave 0.29 vs 0.41 | Local 8-epoch MSE: attention 0.797 vs baseline 0.789; microwave 0.407 | Keep report numbers as official midterm; do not overwrite with local unless Yang approves |
| Huber loss not executed / O4 unvalidated | Local 2×2 shows MSE better than Huber | Yang must review; report's O4 statement needs an update if the local experiment is accepted |
| WHITED uses Hilbert V-I trajectories | Local WHITED uses 19 handcrafted features + RF | Jin/Yang must provide the official Hilbert V-I pipeline or correct the report wording |
| REDD/PLAID preprocessing completed by M1 | No REDD/PLAID artifacts in this workspace | Do not claim local REDD/PLAID; obtain M1 data |
| 10 ONNX models, 18.64 ms | 10 ONNX exist locally; measured 40–75 ms | Re-measure and correct the report |

## 5. Data dependencies / gaps

- `data/raw/ukdale.h5` (~6.3 GB) is local and gitignored.
- `data/processed/` is local; not in git.
- **No REDD, no PLAID** in this workspace.
- **No official M1 preprocessed data**; local normalization/splits may differ from Jin's pipeline.
- `house2` is used as a **test set only**; no house2 training.
- WHITED baseline is feature-based RF; **no Hilbert V-I tensor** and **no raw-waveform CNN** locally.

## 6. Transfer checklist (Yang)

- [ ] Review `ml/models/seq2point.py` and `ml/train/train_one.py`; confirm architecture/loss.
- [ ] Replace local `data/processed` with M1 official data; re-run normalization/stats.
- [ ] Reproduce 3-seed runs (7/17/42), not just seed 42.
- [ ] Decide whether the 8-epoch MSE results or the report's 3-epoch results are the canonical midterm numbers.
- [ ] Re-run WHITED with the official Hilbert V-I pipeline; keep RF as baseline only.
- [ ] Take ownership of `ml/checkpoints/*.json` and `MODEL_EVIDENCE.md` after verification.
- [ ] Do not merge local provisional numbers into the final report without a signed note in the repo.

## 7. What YSB keeps

- `backend/`, `mobile/`, `openapi/`, `scripts/smoke_api.py`
- `HANDOFF/ENGINEERING_MOBILE.md`, `HANDOFF/EVIDENCE.md`
- The local `ml/` tree remains in the repo for traceability, but ownership is Yang's.
