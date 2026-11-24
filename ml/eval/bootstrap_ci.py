"""Block-bootstrap confidence intervals for MAE / RMSE.

The test windows overlap (stride 30 = 3 min), so an i.i.d. bootstrap would be
too optimistic. We resample contiguous blocks of 30 windows and report a 95%
percentile interval. Event-F1 is reported as a point estimate with its positive
window count; it is not bootstrapped because concatenating blocks invents
boundary events.
"""

from __future__ import annotations

import argparse
import json

import numpy as np
import torch

from eval.evaluate import predict_split
from preprocess.config import ROOT
from train.metrics import event_scores, mae, rmse

CKPT_DIR = ROOT / "ml" / "checkpoints"
OUT = CKPT_DIR / "metrics_ci.json"


def block_ci(y_true: np.ndarray, y_pred: np.ndarray, fn, block=30, n_boot=500, seed=42):
    n = len(y_true)
    starts = np.arange(0, n - block + 1, block)
    rng = np.random.default_rng(seed)
    values = []
    for _ in range(n_boot):
        chosen = rng.choice(starts, size=len(starts), replace=True)
        idx = np.concatenate([np.arange(s, s + block) for s in chosen])
        values.append(fn(y_true[idx], y_pred[idx]))
    values = np.asarray(values)
    return {
        "mean": float(values.mean()),
        "low": float(np.percentile(values, 2.5)),
        "high": float(np.percentile(values, 97.5)),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--models", nargs="+", default=["attention", "baseline", "dilated"])
    parser.add_argument("--n-boot", type=int, default=500)
    parser.add_argument("--block", type=int, default=30)
    args = parser.parse_args()

    rows = []
    for model_name in args.models:
        for pt in sorted(CKPT_DIR.glob(f"*_{model_name}*.pt")):
            ckpt = torch.load(pt, map_location="cpu", weights_only=False)
            run_name = ckpt.get("run_name", pt.stem)
            appliance = ckpt["appliance"]
            y_true, y_pred = predict_split(ckpt, "test")
            threshold = float(ckpt.get("on_threshold", 0))
            ev = event_scores(y_true, y_pred, threshold, tol=10)
            rows.append(
                {
                    "appliance": appliance,
                    "model": model_name,
                    "run": run_name,
                    "loss": ckpt.get("loss", "weighted_huber"),
                    "mae": float(mae(y_true, y_pred)),
                    "mae_ci": block_ci(y_true, y_pred, mae, args.block, args.n_boot),
                    "rmse": float(rmse(y_true, y_pred)),
                    "rmse_ci": block_ci(y_true, y_pred, rmse, args.block, args.n_boot),
                    "event_f1": float(ev["f1"]),
                    "positive_windows": int(np.sum(y_true > threshold)),
                    "n_windows": int(len(y_true)),
                }
            )
            print(appliance, model_name, "done", flush=True)

    OUT.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    print("wrote", OUT, "rows", len(rows))


if __name__ == "__main__":
    main()
