"""Recompute ablation CSV from saved checkpoints on test split (fixed SAE)."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np
import torch

from models.seq2point import build_model
from preprocess.config import ON_THRESHOLDS, PROCESSED_DIR, ROOT, WINDOW_SIZE
from train.dataset import WindowDataset
from train.metrics import evaluate_all
from train.train_one import resolve_file

CKPT = ROOT / "ml" / "checkpoints"


def main() -> None:
    man = json.loads((PROCESSED_DIR / "dataset_manifest.json").read_text(encoding="utf-8"))
    rows = []
    for pt in sorted(CKPT.glob("*.pt")):
        ckpt = torch.load(pt, map_location="cpu", weights_only=False)
        app = ckpt["appliance"]
        model_name = ckpt["model_name"]
        if app not in man["files"] or "test" not in man["files"][app]:
            continue
        ds = WindowDataset(resolve_file(man, app, "test"))
        model = build_model(model_name, WINDOW_SIZE)
        model.load_state_dict(ckpt["state_dict"])
        model.eval()
        x = torch.from_numpy(ds.x)
        with torch.no_grad():
            pred = model(x).numpy()
        stats = ckpt["stats"]
        y_pred = pred * stats["y_std"] + stats["y_mean"]
        y_true = ds.y * stats["y_std"] + stats["y_mean"]
        m = evaluate_all(y_true, y_pred, ON_THRESHOLDS[app])
        rows.append(
            {
                "appliance": app,
                "model": model_name,
                "mae": m["mae"],
                "sae": m["sae"],
                "f1": m["f1"],
                "accuracy": m["accuracy"],
            }
        )
        print(app, model_name, m)
    with (CKPT / "ablation_metrics.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["appliance", "model", "mae", "sae", "f1", "accuracy"])
        w.writeheader()
        w.writerows(rows)
    (CKPT / "ablation_metrics.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
