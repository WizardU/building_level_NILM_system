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


def event_scores(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    threshold: float,
    tol: int = 50,
) -> dict[str, float]:
    """Event-level P/R/F1 based on rising edges (ON transitions).

    A predicted event matches a true event if it falls within ±tol samples.
    This is more application-relevant than per-sample scores.
    """
    def rising_edges(signal):
        on = np.asarray(signal) >= threshold
        return np.flatnonzero(np.diff(on.astype(np.int8)) == 1) + 1

    true_ev = rising_edges(y_true)
    pred_ev = rising_edges(y_pred)
    matched, used = 0, set()
    for e in pred_ev:
        if len(true_ev):
            j = int(np.argmin(np.abs(true_ev - e)))
            if abs(int(true_ev[j]) - e) <= tol and j not in used:
                matched += 1
                used.add(j)
    p = matched / len(pred_ev) if len(pred_ev) else 0.0
    r = matched / len(true_ev) if len(true_ev) else 0.0
    f1 = 2 * p * r / max(p + r, 1e-9)
    return {"precision": float(p), "recall": float(r), "f1": float(f1)}


def evaluate_all(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    on_threshold: float,
    event_tol: int = 50,
) -> dict[str, float]:
    out = {
        "mae": mae(y_true, y_pred),
        "sae": sae(y_true, y_pred),
    }
    out.update({f"state_{k}": v for k, v in classification_scores(y_true, y_pred, on_threshold).items()})
    out.update({f"event_{k}": v for k, v in event_scores(y_true, y_pred, on_threshold, event_tol).items()})
    return out
