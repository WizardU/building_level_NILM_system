# Checkpoints index

> Binary `.pt`, `.onnx`, `.joblib` files are **gitignored**. The tracked JSON/CSV files are the evidence.
> See `HANDOFF/ALGORITHM_PROVISIONAL.md`: the algorithm work is provisional and owned by Yang Yifei.

## Production demo (attention + MSE)

| File | Used by | Notes |
|---|---|---|
| `{appliance}_attention.onnx` | FastAPI / ONNX Runtime | 5 files; current deployed variant |
| `{appliance}_attention.json` | model metadata | stats, threshold, params |
| `{appliance}_baseline.onnx` | comparison only | 5 files; not the deployed path |

`appliance` ∈ `fridge`, `kettle`, `microwave`, `dishwasher`, `washing_machine`.

## Ablation / provisional artifacts (not deployed)

| Pattern | Purpose |
|---|---|
| `*_baseline_mse.pt`, `*_attention_mse.pt`, `*_dilated_mse.pt` | 3-model / loss ablation |
| `*_dilated.pt` | dilated-only, weighted Huber |
| `microwave_attention_wmse25.pt` | 25× positive-weighted microwave experiment |
| `ablation_metrics.json/csv` | all test-set rows (MSE + weighted Huber) |
| `loss_ablation.json` | 2×2 summary |
| `cross_house_house2.json` | house1 → house2 test |
| `metrics_ci.json` | block bootstrap CI |
| `training_runs.json` / `training_runs_mse.json` | per-epoch histories |
| `whited_metrics.json` / `whited_index.json` | WHITED RF baseline |

## Reproduction warning

- The local data (`data/processed`) is not the official M1 output.
- The report's official midterm numbers are 3-epoch; local numbers are 8-epoch MSE.
- Do not mix them without a note from Yang.
- If `*.onnx` is missing, `/readyz` falls back to `heuristic`; do not claim ONNX.
