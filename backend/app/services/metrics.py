"""Read the model evaluation tables produced by ``ml/eval``."""

from __future__ import annotations

import json
from pathlib import Path

from app.config import settings


def _rows() -> list[dict]:
    directory = Path(settings.model_dir)
    for name in ("evaluation_test.json", "ablation_metrics.json"):
        path = directory / name
        if path.exists():
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                if isinstance(data, list):
                    return data
            except (json.JSONDecodeError, OSError):
                continue
    return []


def _normalize(row: dict) -> dict:
    """Accept both the old (f1/accuracy) and new (state_*/event_*) schemas."""
    return {
        "appliance": row.get("appliance", ""),
        "model": row.get("model", ""),
        "run": row.get("run", ""),
        "loss": row.get("loss", "weighted_huber"),
        "split": row.get("split", "test"),
        "samples": int(row.get("samples", 0) or 0),
        "mae": float(row.get("mae", 0.0) or 0.0),
        "sae": float(row.get("sae", 0.0) or 0.0),
        "state_f1": float(row.get("state_f1", row.get("f1", 0.0)) or 0.0),
        "state_precision": float(row.get("state_precision", 0.0) or 0.0),
        "state_recall": float(row.get("state_recall", 0.0) or 0.0),
        "state_accuracy": float(row.get("state_accuracy", row.get("accuracy", 0.0)) or 0.0),
        "event_f1": float(row.get("event_f1", 0.0) or 0.0),
        "event_precision": float(row.get("event_precision", 0.0) or 0.0),
        "event_recall": float(row.get("event_recall", 0.0) or 0.0),
        "on_threshold": float(row.get("on_threshold", 0.0) or 0.0),
        "params": int(row.get("params", 0) or 0),
    }


def _canonical_rows() -> list[dict]:
    """One row per appliance/model: prefer MSE when it exists.

    ``ablation_metrics.json`` contains both the loss ablation and the main
    models. The API should expose one comparable configuration per model, not
    silently average MSE and Huber rows together.
    """
    rows = [_normalize(r) for r in _rows()]
    selected = {}
    for model in {r["model"] for r in rows}:
        model_rows = [r for r in rows if r["model"] == model]
        selected[model] = "mse" if any(r["loss"] == "mse" for r in model_rows) else "weighted_huber"
    return [r for r in rows if r["loss"] == selected.get(r["model"])]


def all_rows() -> list[dict]:
    return [_normalize(r) for r in _rows()]


def rows_for_model(model: str) -> list[dict]:
    return [r for r in _canonical_rows() if r["model"] == model]


def average(model: str) -> dict:
    rows = rows_for_model(model)
    if not rows:
        return {}
    keys = ("mae", "sae", "state_f1", "event_f1", "state_precision", "state_recall")
    return {key: round(sum(r[key] for r in rows) / len(rows), 4) for key in keys}


def model_names() -> list[str]:
    return sorted({r["model"] for r in all_rows()})


def as_summary() -> dict:
    rows = _canonical_rows()
    models = model_names()
    return {
        "models": models,
        "averages": {m: average(m) for m in models},
        "rows": rows,
        "samples": max((r["samples"] for r in rows), default=0),
    }
