"""Dataset cards and offline experiment results."""

from __future__ import annotations

import json
from pathlib import Path

from fastapi import APIRouter, Depends

from app import models
from app.config import settings
from app.response import ok
from app.security import get_current_user

router = APIRouter(tags=["Datasets"])


def _read(name: str) -> dict | None:
    path = Path(settings.model_dir) / name
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


@router.get("/datasets/whited")
def whited(_: models.User = Depends(get_current_user)):
    index = _read("whited_index.json")
    metrics = _read("whited_metrics.json")
    if index is None and metrics is None:
        return ok(
            {
                "available": False,
                "hint": "Run: cd ml && python -m preprocess.whited",
            }
        )
    return ok({"available": True, "index": index, "metrics": metrics})
