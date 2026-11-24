# Evidence audit — what is actually completed

**Audit date:** 2026-11-25  
**Branch:** `handoff/usp-engineering-midterm`  
**Canonical evidence tag:** `midterm-2026-11-30-evidence` (`72ed7bf`) for the metrics;  
handoff tag `handoff-usp-2026-11-25` for the repo package.

## 1. Bottom line

**All current model evidence is 8 epoch.** The **3 epoch** text is only in the Progress Report and is stale.
The report must be revised, or it will contradict the deck, `MODEL_EVIDENCE.md`, and every checkpoint history.

| Item | Actual | Evidence |
|---|---|---|
| Baseline MSE training | **8 epoch** | `ml/checkpoints/training_runs_mse.json` (15 runs, history len 8) |
| Attention MSE training | **8 epoch** | `attention_mse_runs.json` (5 runs, history len 8) |
| Dilated MSE training | **8 epoch** | `dilated_mse_runs.json` (5 runs, history len 8) |
| Weighted-Huber runs | **8 epoch** | `training_runs.json` (10 runs, history len 8) |
| Loss 2×2 | **8 epoch** | `loss_ablation_runs.json` (5 runs, history len 8) |
| Metrics table | 8 epoch | `ablation_metrics.json`, 30 rows |
| Cross-house | 8 epoch models | `cross_house_house2.json`, 15 rows |
| Microwave 25× | 8 epoch base + extra run | `microwave_wmse25.json` |
| ONNX artifacts | 10 models, exported 2026-11-20 | `ml/checkpoints/*.onnx` |
| **Progress Report** | **3 epoch** | docx §abstract, §1, §5, Appendix D |

## 2. Current 8-epoch numbers (canonical)

| Model | MAE | RMSE | State F1 | Event F1 |
|---|---:|---:|---:|---:|
| Baseline | 12.45 W | 62.92 W | **0.790** | 0.789 |
| Dilated | 12.99 W | 64.11 W | 0.733 | 0.786 |
| Attention | **10.45 W** | **62.25 W** | 0.762 | **0.797** |

Per appliance, attention:

| Appliance | MAE | State F1 | Event F1 |
|---|---:|---:|---:|
| Fridge | 22.70 | 0.815 | 0.878 |
| Kettle | 6.98 | 0.846 | 0.860 |
| Microwave | 5.91 | 0.319 | 0.407 |
| Dishwasher | 6.96 | 0.878 | 0.895 |
| Washing machine | 9.69 | 0.950 | 0.943 |

## 3. What the Progress Report currently says (stale)

The report's 3-epoch claims are at these locations:

- Abstract: "3 epochs", attention 11.4 W / Event 0.71 / State 0.68, baseline 0.76, microwave 0.29 vs 0.41.
- §1 O3: "3 epochs", 0.71 / 0.68 / 11.4 W, "dilated not integrated".
- §1 O5: "target missed", 0.71 vs 0.76, RMSE/SAE pending.
- §2 change 1: "capping initial real-data attention training at 3 epochs".
- §5: Figure 5.2 "3 epochs", "validation Event F1 plateau at 0.58".
- Appendix D: "3-epoch run", loss 0.92→0.72→0.66.
- Table 1 (O2/O3/O5), Table 3 (M2 "3 epochs"), Table 5, Table 6, Table 7.

None of these match the current artifacts.

## 4. What is genuinely not completed

Do not claim these as done:

- 3-seed evaluation (only seed 42)
- Seq2Seq baseline
- automatic early stopping
- REDD/PLAID model training
- WHITED raw-waveform CNN (only RF baseline)
- Redis/PostgreSQL, Modbus/MQTT, native iOS/Android, pytest/CI
- independent non-overlapping test set; current test windows overlap with stride 30

## 5. Stale commit reference

`MODEL_EVIDENCE.md` previously said `f6a643e`; that commit is **not an ancestor** of the current branch/tag.
Use `midterm-2026-11-30-evidence` (`72ed7bf`) or the handoff tag `handoff-usp-2026-11-25` (`e5ab9a0`).
This audit updates that reference.

## 6. Decision

Use **8 epoch** as the current completed evidence in:

- Progress Report (replace 3-epoch numbers)
- deck (`NILM-pre11.25.pptx` already 8 epoch)
- `MODEL_EVIDENCE.md`
- `HANDOFF` docs

Keep "3 epoch" only in a clearly labelled “earlier preliminary run” note, or remove it entirely.
