# Midterm ML work (YSB) → future improvement handoff (Yang)

> **Ownership correction:** the ML training, ONNX export, evaluation and WHITED RF baseline that are in the
> midterm progress report are **U SENGPAN's work**. They are no longer labelled "not YSB's contribution".
> The **future improvements** in W5+ (dilated/Huber, 3-seed, cross-house, REDD/PLAID, WHITED CNN) are handed
> to Yang Yifei. M1 official preprocessing remains Jin Xinyi's.

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

So: **local preprocessing exists and is methodologically equivalent, but it is not the exact figure / official
M1 artifact.** Do not put the local `data/processed` in the report as Jin's M1 deliverable. If the figure came
from Jin's pipeline, the local copy must be replaced before final experiments.

## 2. What is YSB's midterm ML work (owned)

- `ml/models/seq2point.py`: baseline, dilated, attention definitions
- `ml/train/train_one.py`, `train_all.py`: training loop, validation loss, threshold calibration
- `ml/eval/evaluate.py`: MAE/SAE/state/event metrics
- 10 ONNX models (5 attention + 5 baseline)
- WHITED RF baseline: 19 features, 400 trees, device holdout
- Midterm report's 3-epoch results: attention 0.71 vs baseline 0.76 Event F1, microwave 0.29/0.41, WHITED 44.1%

## 3. What was added after the report (post-report evidence)

These are **later local experiments**, useful as improvement evidence but not the report's official midterm numbers:

| Experiment | Result |
|---|---|
| 8-epoch MSE, three models | attention 0.797 / baseline 0.789 / dilated 0.786 Event F1 |
| 2×2 loss | MSE beats weighted Huber; attention MSE 0.797 vs weighted 0.779 |
| House1 → house2 | attention 0.775 / baseline 0.814 Event F1; attention lower MAE |
| Microwave 25× weighted MSE | 0.407 → 0.494 Event F1, recall 0.68 |
| Block bootstrap | MAE CI around the point estimates; overlapping-window caveat |

Full numbers: `MODEL_EVIDENCE.md`; artifacts: `ml/checkpoints/*.json`.

## 4. What is Yang's future scope (W5+)

- dilated-only + loss ablation at 3 seeds (report says O3/O4 still open)
- 3-seed mean±SD and early stopping
- cross-house/cross-dataset (REDD/PLAID)
- WHITED raw-waveform CNN
- final model selection and thesis claims

The local 8-epoch experiments can be given to Yang as a starting point, but Yang owns the final reproduction.

## 5. Report wording to correct

| Report currently says | Should say |
|---|---|
| M2 model/eval owner = Yang Yifei | **Midterm M2 training/ONNX/WHITED = U SENGPAN; W5+ improvements = Yang Yifei** |
| `[TBD: YSB backend & mobile commits]` | branch/tag/commit evidence (see `EVIDENCE.md`) |
| "SQLite/PostgreSQL + Redis", "18.64 ms" | SQLite only; 40–75 ms measured locally |
| WHITED "Hilbert V-I trajectories" | local baseline uses 19 handcrafted features + RF; official Hilbert pipeline must come from M1/M2 owner |

## 6. Data dependencies / gaps

- `data/raw/ukdale.h5` (~6.3 GB) local, gitignored
- `data/processed/` local, gitignored, **not official M1**
- **No REDD, no PLAID** here
- house2 is **test-only**, not training
- WHITED has no Hilbert V-I tensor / raw-waveform CNN here
- Midterm models use **3 epochs** in the report; local 8-epoch results are separate

## 7. Handoff checklist

- [ ] YSB keeps the midterm 3-epoch/10-ONNX/WHITED-RF claim in the report.
- [ ] Report contribution table updated: midterm M2 = U SENGPAN; W5+ M2 = Yang.
- [ ] Yang receives `ml/` code, local `data/processed` path, and `MODEL_EVIDENCE.md`.
- [ ] Jin confirms official M1 preprocessing path; local copy is not used as M1 evidence.
- [ ] Future improvements are not merged into the midterm report as if already complete.
