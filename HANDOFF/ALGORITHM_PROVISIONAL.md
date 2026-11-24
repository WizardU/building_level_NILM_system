# Midterm ML work (USP) → future improvement handoff (Yang)

> **Current evidence is 8 epoch.** The Progress Report's 3-epoch text is stale and must be replaced
> (see `EVIDENCE_AUDIT.md` and `REPORT_CORRECTION.md`). The 8-epoch baseline/attention/dilated runs,
> the 2×2 loss ablation, cross-house and microwave 25× experiments are the current completed artifacts.

## 1. Local preprocessing: yes, but not identical to the figure

Local artifacts:

- `ml/preprocess/ukdale.py` — custom HDF5 reader (no NILMTK)
- `data/processed/dataset_manifest.json` — 2,606,400 samples, 6 s, 2014-01-01→2014-06-30
- `data/processed/ukdale_house1_*_{train,val,test}.h5` — 15 files (5 appliances × 3 splits)
- window 599, centre target, Z-score, chronological 70/15/15
- 60,797 train / 13,013 val / 13,013 test windows per appliance

The screenshot (`Preprocessing UK-DALE`) is **the same design** (599-point window, centre marker, raw/Z-score
histograms) but **not the same window/artifact**:

| Check | Screenshot | Local train #10000 | Local val #10000 | Local test #10000 |
|---|---|---|---|---|
| Fridge target at centre | 1.0 W | 0.0 W | 0.0 W | 91.0 W |
| Window shape | spikes ~500/2200 W | 465–893 W | 149–238 W | 359–3307 W |
| Center mains | ~2200 W region | 484 W | 160 W | 663 W |

So: local preprocessing exists and is methodologically equivalent, but it is **not the exact figure /
official M1 artifact**. Do not put local `data/processed` in the report as Jin's M1 deliverable. If the figure
came from Jin's pipeline, the local copy must be replaced before final experiments.

## 2. Current completed ML evidence (8 epoch)

- `ml/models/seq2point.py`: baseline, dilated, attention definitions
- `ml/train/train_one.py`, `train_all.py`: training loop, validation loss, threshold calibration
- `ml/eval/evaluate.py`: MAE/RMSE/SAE/state/event metrics
- 10 ONNX models (5 attention + 5 baseline), exported 2026-11-20
- WHITED RF baseline: 19 features, 400 trees, device holdout

| Model | MAE | RMSE | State F1 | Event F1 |
|---|---:|---:|---:|---:|
| Baseline | 12.45 W | 62.92 W | **0.790** | 0.789 |
| Dilated | 12.99 W | 64.11 W | 0.733 | 0.786 |
| Attention | **10.45 W** | **62.25 W** | 0.762 | **0.797** |

- Attention vs baseline: MAE **−16.1%**, Event F1 +0.008, State F1 −0.028.
- Dilated-only does not beat baseline; the gain is the attention combination.
- 2×2 loss: MSE beats weighted Huber at 8 epochs (attention MSE 0.797 vs weighted 0.779).
- Cross-house: attention Event 0.775 / MAE 13.97; baseline Event 0.814 / MAE 15.06.
- Microwave: attention Event 0.407; 25× weighted MSE → 0.494 (recall 0.68), offline.
- WHITED: 44.1% top-1 / 27.0% macro F1 / 71.8% top-3; 18/40 classes evaluable.

## 3. The 3-epoch text is stale

The Progress Report says 3 epochs, 0.71/0.76 Event F1, 11.4 W MAE, microwave 0.29/0.41. Those values
**do not exist in the current artifacts**. The current histories are all 8 steps:

- `training_runs_mse.json`: 15 runs × 8
- `attention_mse_runs.json`: 5 × 8
- `dilated_mse_runs.json`: 5 × 8
- `training_runs.json`: 10 × 8
- `loss_ablation_runs.json`: 5 × 8

Do not keep both versions as "current". Replace the report's 3-epoch claims with the 8-epoch values
(exact replacements in `REPORT_CORRECTION.md`) or label the 3-epoch run explicitly as an earlier,
superseded preliminary run.

## 4. What is Yang's future scope (W5+)

- 3-seed mean±SD (7/17/42) and early stopping
- REDD/PLAID cross-dataset and domain adaptation
- WHITED raw-waveform CNN
- final model selection and thesis claims

The 8-epoch code/results are handed over as the starting point; Yang owns the final reproduction.

## 5. Data dependencies / gaps

- `data/raw/ukdale.h5` (~6.3 GB) local, gitignored
- `data/processed/` local, gitignored, **not official M1**
- **No REDD, no PLAID** here
- house2 is **test-only**, not training
- WHITED has no Hilbert V-I tensor / raw-waveform CNN here
- Only seed 42; no 3-seed; no Seq2Seq; no automatic early stopping

## 6. Handoff checklist

- [ ] Report 3-epoch values replaced by 8-epoch values (`REPORT_CORRECTION.md`).
- [ ] Report O3/O5 status updated: attention Event 0.797 vs baseline 0.789; MAE target met 16.1%.
- [ ] Report contribution table: midterm M2 = U SENGPAN; W5+ M2 = Yang.
- [ ] Yang receives `ml/` code, local `data/processed` path, and `MODEL_EVIDENCE.md`.
- [ ] Jin confirms official M1 preprocessing path; local copy is not used as M1 evidence.
- [ ] 3-seed and cross-dataset remain future work, not claimed.
