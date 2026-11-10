"""Evaluate saved checkpoints on a split and return a flat metrics record."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import torch
from torch.utils.data import DataLoader

from models.seq2point import build_model
from preprocess.config import ON_THRESHOLDS, PROCESSED_DIR, WINDOW_SIZE
from train.dataset import WindowDataset
from train.metrics import evaluate_all, event_scores
from train.train_one import resolve_file

FIELDS = [
    "appliance",
    "model",
    "split",
    "samples",
    "mae",
    "sae",
    "state_accuracy",
    "state_precision",
    "state_recall",
    "state_f1",
    "event_precision",
    "event_recall",
    "event_f1",
    "on_threshold",
    "params",
]


def load_manifest(path: Path | None = None) -> dict:
    p = path or (PROCESSED_DIR / "dataset_manifest.json")
    return json.loads(Path(p).read_text(encoding="utf-8"))


def predict_split(checkpoint: dict, split: str, batch_size: int = 256) -> tuple[np.ndarray, np.ndarray]:
    """Return ``(y_true_watts, y_pred_watts)`` for one split."""
    manifest = load_manifest()
    appliance = checkpoint["appliance"]
    model = build_model(checkpoint["model_name"], checkpoint.get("window_size", WINDOW_SIZE))
    model.load_state_dict(checkpoint["state_dict"])
    model.eval()
    dataset = WindowDataset(resolve_file(manifest, appliance, split))
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=False)
    stats = checkpoint["stats"]
    preds, trues = [], []
    with torch.no_grad():
        for x, y in loader:
            preds.append(model(x).numpy())
            trues.append(y.numpy())
    y_pred = np.concatenate(preds) * stats["y_std"] + stats["y_mean"]
    y_true = np.concatenate(trues) * stats["y_std"] + stats["y_mean"]
    return y_true, np.clip(y_pred, 0.0, None)


def calibrate_threshold(y_true: np.ndarray, y_pred: np.ndarray, default: float) -> tuple[float, float]:
    """Pick the ON threshold that maximises event-level F1 on a validation split."""
    if len(y_pred) == 0:
        return default, 0.0
    positives = y_pred[y_pred > 0]
    if positives.size == 0:
        return default, 0.0
    candidates = np.unique(
        np.concatenate(
            [
                np.quantile(positives, np.linspace(0.50, 0.995, 40)),
                np.array([default, 25.0, 50.0, 100.0, 200.0, 500.0]),
            ]
        )
    )
    best_t, best_f1 = default, -1.0
    for t in candidates:
        score = event_scores(y_true, y_pred, float(t))["f1"]
        if score > best_f1:
            best_t, best_f1 = float(t), float(score)
    return best_t, float(best_f1)


def evaluate_checkpoint(
    pt_path: str | Path,
    split: str = "test",
    threshold: float | None = None,
) -> dict:
    checkpoint = torch.load(pt_path, map_location="cpu", weights_only=False)
    appliance = checkpoint["appliance"]
    on_threshold = float(
        threshold
        if threshold is not None
        else checkpoint.get("on_threshold", ON_THRESHOLDS[appliance])
    )
    y_true, y_pred = predict_split(checkpoint, split)
    metrics = evaluate_all(y_true, y_pred, on_threshold)
    params = int(sum(p.numel() for p in build_model(checkpoint["model_name"]).parameters()))
    record = {
        "appliance": appliance,
        "model": checkpoint["model_name"],
        "split": split,
        "samples": int(len(y_true)),
        "mae": round(float(metrics["mae"]), 3),
        "sae": round(float(metrics["sae"]), 4),
        "state_accuracy": round(float(metrics["state_accuracy"]), 4),
        "state_precision": round(float(metrics["state_precision"]), 4),
        "state_recall": round(float(metrics["state_recall"]), 4),
        "state_f1": round(float(metrics["state_f1"]), 4),
        "event_precision": round(float(metrics["event_precision"]), 4),
        "event_recall": round(float(metrics["event_recall"]), 4),
        "event_f1": round(float(metrics["event_f1"]), 4),
        "on_threshold": round(on_threshold, 2),
        "params": params,
    }
    return record


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Evaluate checkpoints on a split")
    parser.add_argument("--glob", default="*.pt")
    parser.add_argument("--split", default="test")
    args = parser.parse_args()
    from preprocess.config import ROOT

    ckpt_dir = ROOT / "ml" / "checkpoints"
    rows = [evaluate_checkpoint(p, args.split) for p in sorted(ckpt_dir.glob(args.glob))]
    for row in rows:
        print(json.dumps(row, ensure_ascii=False))
    out = ckpt_dir / f"evaluation_{args.split}.json"
    out.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
