"""Export ablation + generalization placeholder tables for thesis figures."""

from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CKPT = ROOT / "ml" / "checkpoints"
OUT = ROOT / "ml" / "eval" / "thesis_exports"
OUT.mkdir(parents=True, exist_ok=True)


def main() -> None:
    ablation = CKPT / "ablation_metrics.json"
    if ablation.exists():
        rows = json.loads(ablation.read_text(encoding="utf-8"))
        (OUT / "ablation_metrics.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")
        with (OUT / "ablation_metrics.csv").open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["appliance", "model", "mae", "sae", "f1", "accuracy"])
            w.writeheader()
            w.writerows(rows)
    else:
        rows = []

    # Generalization template (fill when REDD / cross-house runs exist)
    gen = [
        {
            "train": "synth_house1 / UK-DALE-1",
            "test": "synth_house1 holdout",
            "model": "attention",
            "mae": _avg(rows, "attention", "mae"),
            "f1": _avg(rows, "attention", "f1"),
            "note": "same-domain",
        },
        {
            "train": "synth_house1 / UK-DALE-1",
            "test": "REDD / UK-DALE-2 (TODO)",
            "model": "attention",
            "mae": None,
            "f1": None,
            "note": "cross-domain placeholder — run ukdale.py + train_all",
        },
    ]
    (OUT / "generalization.json").write_text(json.dumps(gen, indent=2), encoding="utf-8")
    with (OUT / "generalization.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["train", "test", "model", "mae", "f1", "note"])
        w.writeheader()
        w.writerows(gen)

    md = OUT / "README.md"
    md.write_text(
        "# Thesis exports\n\n"
        "- `ablation_metrics.csv`: baseline → dilated → attention\n"
        "- `generalization.csv`: cross-house / REDD slots\n"
        "Paste into thesis tables or Evaluation page screenshots.\n",
        encoding="utf-8",
    )
    print(f"Wrote exports under {OUT}")


def _avg(rows, model, field):
    xs = [r[field] for r in rows if r.get("model") == model]
    return round(sum(xs) / len(xs), 4) if xs else None


if __name__ == "__main__":
    main()
