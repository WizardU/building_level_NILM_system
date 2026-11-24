# Report correction — contribution ownership

The progress report's current contribution table says **M2 model/eval = Yang Yifei**. That is not the
midterm reality: the **existing ML training, ONNX export, evaluation and WHITED RF baseline were done by
U SENGPAN**. Yang owns the **W5+ improvements** only.

This file gives exact wording to change; it does not rewrite the submitted docx.

## 1. Abstract / contributions sentence

Add after the "system engineering side" sentence:

> The midterm ML training, ONNX export, evaluation and WHITED RF baseline were implemented by U SENGPAN;
> the W5+ model improvements (dilated/Huber, 3-seed, cross-house/cross-dataset, WHITED CNN) are assigned to
> Yang Yifei.

## 2. Contributions table

| Member | Current wording | Change to |
|---|---|---|
| Jin Xinyi | Data Pipeline & Web Frontend Lead | unchanged (official M1/M4) |
| Yang Yifei | AI & Algorithm Modeling Lead | **AI & Algorithm Modeling Lead (W5+ improvement)** |
| U SENGPAN | Backend API & Mobile App Lead | **Backend & Mobile Lead + Midterm ML Training/ONNX/Evaluation** |

## 3. M2 module rows

Where the report lists M2.1/M2.2/M2.3 with owner `Yang Yifei`, use:

| Module | Owner |
|---|---|
| M2.1 Baseline Seq2Point training + ONNX | **U SENGPAN** |
| M2.2 Attention training + ONNX + threshold calibration | **U SENGPAN** |
| M2.3 WHITED RF baseline (19 features, 400 trees, 20-device holdout) | **U SENGPAN** |
| W5+ dilated/Huber ablation, 3-seed, cross-house, REDD/PLAID, WHITED CNN | **Yang Yifei** |

The O2/O3/O4/O5 status in §1 stays as the report's 3-epoch snapshot; do not silently replace it with the
local 8-epoch results. Those are post-report experiments (see `ALGORITHM_PROVISIONAL.md`).

## 4. `[TBD]` commit row

Replace:

> `[TBD: USP backend & mobile commits]`

with:

> U SENGPAN — midterm M2 ML training/ONNX/eval + M3 backend + M5 mobile H5:
> `handoff/usp-engineering-midterm`, tag `handoff-usp-2026-11-25`,
> commit `<short-hash>` (course repo mirror: `<course-commit>`).
> Evidence: 10 ONNX models, 3-epoch report tables, WHITED RF 44.1%, 21/21 API checks,
> `report_build/shots/mobile_analytics.png`, `openapi/NILM.json`.

## 5. M1 / preprocessing

Keep **M1 official preprocessing = Jin Xinyi**. USP's local `ml/preprocess` + `data/processed` is a
**fallback copy**, not the official M1 deliverable. The figure "Preprocessing UK-DALE" may be Jin's
pipeline output; the local window #10000 does not match it exactly (see `ALGORITHM_PROVISIONAL.md` §1).

## 6. One-sentence consistency check

After editing, the report should be internally consistent:

> Midterm M2 training = U SENGPAN; midterm M3/M5 = U SENGPAN; W5+ M2 improvements = Yang Yifei;
> M1/M4 = Jin Xinyi; all `[TBD]` hashes replaced by branch/tag/commit.
