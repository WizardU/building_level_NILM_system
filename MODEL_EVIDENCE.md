# Model evidence — 2026-11-20

All numbers are test-set values. The three models below use **MSE** (the proposal's baseline loss), same 8 epochs and seed 42; the loss ablation is separate.

## 1. Three-model ablation (UK-DALE house 1, test 13,013 windows/appliance)

| Appliance | Baseline Event F1 | Dilated Event F1 | Attention Event F1 | Baseline MAE | Dilated MAE | Attention MAE |
|---|---:|---:|---:|---:|---:|---:|
| Fridge | 0.901 | 0.890 | 0.878 | 22.61 | 24.09 | 22.70 |
| Kettle | 0.852 | 0.853 | 0.860 | 8.03 | 10.41 | 6.98 |
| Microwave | 0.439 | 0.456 | 0.407 | 7.95 | 7.36 | 5.91 |
| Dishwasher | 0.872 | 0.857 | 0.895 | 12.34 | 7.02 | 6.96 |
| Washing machine | 0.881 | 0.873 | 0.943 | 11.32 | 16.05 | 9.69 |
| **Mean** | **0.789** | **0.786** | **0.797** | **12.45** | **12.99** | **10.45** |

- Attention vs baseline (MSE): Event F1 **0.797 vs 0.789**; MAE **10.45 vs 12.45 W** → **16.1% lower** (proposal target ≥10%: met).
- Dilated-only vs baseline: Event F1 0.786 vs 0.789; dilation alone does not improve the average.
- Baseline still has higher State F1 (0.790 vs 0.762); attention is not uniformly better.

## 2. Loss ablation (2 × 2: baseline/attention × MSE/weighted Huber)

| Model | Loss | MAE | RMSE | State F1 | Event F1 |
|---|---|---:|---:|---:|---:|
| Baseline | MSE | 12.45 | 62.9 | 0.790 | 0.789 |
| Baseline | Weighted Huber | 13.60 | 64.3 | 0.743 | 0.751 |
| Attention | MSE | 10.45 | 62.3 | 0.762 | 0.797 |
| Attention | Weighted Huber | 11.42 | 66.3 | 0.761 | 0.779 |

**Finding:** MSE is stronger than weighted Huber at 8 epochs on this dataset; the weighted loss should not be claimed as an improvement without further tuning.

## 3. Cross-house test: train house 1, test house 2 (44,141 windows/appliance, no retraining)

| Model | House-1 Event F1 | House-2 Event F1 | House-1 MAE | House-2 MAE | House-2 State F1 |
|---|---:|---:|---:|---:|---:|
| Baseline | 0.789 | 0.814 | 12.45 | 15.06 | 0.705 |
| Dilated | 0.786 | 0.696 | 12.99 | 15.87 | 0.615 |
| Attention | 0.797 | 0.775 | 10.45 | 13.97 | 0.667 |

- Attention has the lowest cross-house MAE but its Event F1 drops from 0.797 to 0.775; baseline Event F1 rises to 0.814.
- Cross-house generalization is **not solved**: microwave remains weak, and the ranking of models changes between houses.

## 4. Bootstrap intervals (block bootstrap, 30-window blocks)

| Model | MAE | 95% CI | RMSE | 95% CI |
|---|---:|---|---:|---|
| Baseline | 12.45 | 10.64–14.46 (mean of per-appliance CIs) | 62.9 | — |
| Attention | 10.45 | 8.66–12.45 (mean of per-appliance CIs) | 62.3 | — |
| Dilated | 12.99 | 11.10–15.06 (mean of per-appliance CIs) | 64.1 | — |

> The CI is a block bootstrap over overlapping windows; it is indicative, not a substitute for independent houses. Event F1 is reported as a point estimate with its positive-window count because event matching is not additive across resampled blocks.
