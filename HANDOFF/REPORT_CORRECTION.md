# Report correction — 8-epoch evidence + ownership

**Two independent corrections are needed:**

1. **Epochs:** the report's 3-epoch numbers are stale; all current artifacts are 8 epoch.
2. **Ownership:** midterm M2 training/ONNX/WHITED is **U SENGPAN (USP)**; W5+ improvements are **Yang Yifei**.

This file gives exact replacement text; it does not silently rewrite the submitted docx.

## 1. Canonical 8-epoch numbers

| Model | MAE | RMSE | State F1 | Event F1 |
|---|---:|---:|---:|---:|
| Baseline | 12.45 W | 62.92 W | **0.790** | 0.789 |
| Dilated | 12.99 W | 64.11 W | 0.733 | 0.786 |
| Attention | **10.45 W** | **62.25 W** | 0.762 | **0.797** |

Per-appliance Event F1:

| Appliance | Baseline | Attention | Difference |
|---|---:|---:|---:|
| Fridge | 0.901 | 0.878 | −0.023 |
| Kettle | 0.852 | 0.860 | +0.008 |
| Microwave | 0.439 | 0.407 | −0.032 |
| Dishwasher | 0.872 | 0.895 | +0.023 |
| Washing machine | 0.881 | 0.943 | +0.062 |
| **Mean** | **0.789** | **0.797** | **+0.008** |

## 2. Abstract replacement

Replace the current "3 epochs / 11.4 W / 0.71 / 0.68 / 0.29 vs 0.41" passage with:

> On UK-DALE House 1 (8 epochs), the temporal-attention model achieves an average MAE of 10.45 W and
> improves Dishwasher event F1 from 0.872 to 0.895. Its overall average event F1 is 0.797 (state F1: 0.762),
> slightly above the baseline 1D-CNN (0.789), while the baseline still has the higher state F1 (0.790).
> Microwave remains the weak class (event F1 0.407 vs. baseline 0.439) because it is ON only 0.39% of the
> time. On WHITED, the strict 20-unseen-device hold-out gives 44.1% top-1, 27.0% macro F1 and 71.8% top-3.

## 3. §1 status table (O2–O6)

Recommended status after 8-epoch evidence:

| Objective | Current | Replacement |
|---|---|---|
| O2 baseline | Completed 0.76 Event F1 | **Completed 0.789 Event F1, 12.45 W MAE** |
| O3 attention/dilation | Partially completed, 3 epochs, 0.71, 11.4 W | **Completed: attention 0.797 Event / 0.762 State / 10.45 W; dilated 0.786 Event; 8 epochs** |
| O4 loss ablation | Not validated | **Completed: 2×2 MSE vs weighted Huber; MSE stronger at 8 epochs (attention 0.797 vs 0.779)** |
| O5 metrics/target | Target missed, 0.71 vs 0.76 | **MAE target met: 10.45 vs 12.45 W = 16.1% reduction; RMSE 62.25 vs 62.92; single seed** |
| O6 backend | Completed | unchanged |

Summary sentence:

> **5 completed (O2–O6), 2 partially completed (O1 datasets, O7 Modbus/MQTT/native), 0 missed targets;
> 3-seed and REDD/PLAID remain future work.**

## 4. §1 O3 wording

Replace:

> 3 epochs, avg Event F1 0.71, State 0.68, MAE 11.4 W; dilated not integrated.

with:

> 8 epochs; attention avg Event F1 **0.797**, State F1 **0.762**, MAE **10.45 W**; dilated integrated and
> evaluated (avg Event F1 **0.786**). Attention improves MAE by **16.1%** vs baseline; baseline still wins
> State F1 (0.790 vs 0.762).

## 5. §1 O4 wording

Replace "not yet validated" with:

> 2×2 ablation completed (baseline/attention × MSE/weighted Huber) at 8 epochs. Attention MSE: 10.45 W /
> 0.797 Event F1; attention weighted Huber: 11.42 W / 0.779. MSE is stronger on this dataset; the proposal's
> expected Huber improvement is not supported by this run.

## 6. §1 O5 wording

Replace "target missed" with:

> Target met on MAE: attention 10.45 W vs baseline 12.45 W = **16.1% reduction** (proposal target ≥10%).
> RMSE 62.25 vs 62.92; SAE 0.109 vs 0.204; Event F1 0.797 vs 0.789; State F1 0.762 vs 0.790.
> Caveat: single seed 42; 3-seed mean±SD is still W5+.

## 7. §5 and figures

- Replace "3 epochs" with "8 epochs" everywhere.
- Replace Figure 5.2 (3-epoch loss/Event-F1) with `report_build/figs/fig_training_all.png`
  (8-epoch train/validation loss, 5 appliances).
- Replace "validation Event F1 plateau at 0.58" with the 8-epoch validation curves; do not reuse the
  3-epoch plateau sentence.

## 8. Table 5/6/7

- Table 5: attention MAE 11.4 → **10.45**; baseline 12.1 (TBD) → **12.45**; attention Event 0.71 → **0.797**;
  baseline 0.76 → **0.789**; attention State 0.68 → **0.762**.
- Table 6 per-appliance: use the table in §1 above (Fridge .901/.878, Kettle .852/.860, Microwave .439/.407,
  Dishwasher .872/.895, Washing .881/.943, Mean .789/.797).
- Table 7 macro: baseline .789 vs attention .797 (+.008), not .76 vs .71 (−.05).

## 9. Table 3 / M2 owner

| Module | Owner | Epochs |
|---|---|---|
| M2.1 baseline Seq2Point + ONNX | **U SENGPAN** | 8 |
| M2.2 attention + ONNX + threshold | **U SENGPAN** | 8 |
| M2.3 WHITED RF baseline | **U SENGPAN** | n/a |
| W5+ dilated/Huber/3-seed/cross-house/REDD/PLAID/WHITED CNN | **Yang Yifei** | future |

Replace `[TBD: YYF train/export commit]` / `[TBD: YSB backend & mobile commits]` with:

> U SENGPAN — midterm M2 ML training/ONNX/eval + M3 backend + M5 mobile H5:
> `handoff/usp-engineering-midterm`, tag `handoff-usp-2026-11-25`, commit `e5ab9a0`.
> Evidence: 10 ONNX models, 8-epoch tables, WHITED RF 44.1%, 21/21 API checks, `openapi/NILM.json`.

## 10. Appendix D / training hardware

- "3-Epoch Temporal Attention Run" → **"8-Epoch Temporal Attention Run"**.
- "3-epoch training" → **"8-epoch training"**.
- Delete the 0.92→0.72→0.66 / Event F1 0.48→0.58→0.58 sentence; use the 8-epoch history in
  `ml/checkpoints/attention_mse_runs.json` or `fig_training_all.png`.

## 11. M1 / preprocessing

Keep **M1 official preprocessing = Jin Xinyi**. USP's local `ml/preprocess` + `data/processed` is a
**fallback copy**, not the official M1 deliverable. The "Preprocessing UK-DALE" figure may be Jin's
pipeline output; local window #10000 does not match it exactly (see `EVIDENCE_AUDIT.md` §1).

## 12. Consistency check

After editing:

> epoch = 8; attention Event = 0.797; baseline Event = 0.789; attention MAE = 10.45; baseline MAE = 12.45;
> microwave = 0.407 vs 0.439; O5 target met; 5 completed / 2 partial; midterm M2 = USP; W5+ = Yang.
