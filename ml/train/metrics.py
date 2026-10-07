"""MAE, SAE, Acc, F1 for NILM evaluation."""

from __future__ import annotations

import numpy as np


def mae(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(np.mean(np.abs(y_true - y_pred)))


def sae(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Normalized sum of absolute energy errors (capped for empty/sparse targets)."""
    denom = float(np.sum(np.abs(y_true)))
    if denom < 1e-3:
        # No / tiny energy in window → report 0 rather than explode
        return 0.0 if float(np.sum(np.abs(y_pred))) < 1e-3 else 1.0
    return float(min(np.abs(np.sum(y_pred) - np.sum(y_true)) / denom, 10.0))


def classification_scores(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    threshold: float,
) -> dict[str, float]:
    yt = y_true > threshold
    yp = y_pred > threshold
    tp = int(np.sum(yt & yp))
    fp = int(np.sum(~yt & yp))
    fn = int(np.sum(yt & ~yp))
    tn = int(np.sum(~yt & ~yp))
    acc = (tp + tn) / max(tp + tn + fp + fn, 1)
    prec = tp / max(tp + fp, 1)
    rec = tp / max(tp + fn, 1)
    f1 = 2 * prec * rec / max(prec + rec, 1e-8)
    return {"accuracy": float(acc), "precision": float(prec), "recall": float(rec), "f1": float(f1)}


def evaluate_all(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    on_threshold: float,
) -> dict[str, float]:
    out = {
        "mae": mae(y_true, y_pred),
        "sae": sae(y_true, y_pred),
    }
    out.update(classification_scores(y_true, y_pred, on_threshold))
    return out
