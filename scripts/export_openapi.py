"""Regenerate ``openapi/NILM.json`` from the running FastAPI application.

The generated file is the single source of truth; `openapi/NILM.json` used to be
hand-written and drifted from the implementation.

Usage:
    python scripts/export_openapi.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.main import app  # noqa: E402


def main() -> None:
    spec = app.openapi()
    spec.setdefault("info", {})["description"] = (
        "Building-level NILM API. Generated from the FastAPI app; do not edit by hand. "
        "All timestamps are UTC with a trailing Z."
    )
    destination = ROOT / "openapi" / "NILM.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(spec, indent=2, ensure_ascii=False, sort_keys=True),
        encoding="utf-8",
    )
    print(f"wrote {destination} ({len(json.dumps(spec))} bytes)")


if __name__ == "__main__":
    main()
