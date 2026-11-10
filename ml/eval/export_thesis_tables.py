"""Export ablation + generalization tables for thesis figures."""

from __future__ import annotations

import csv
import json
from pathlib import Path

from eval.evaluate import FIELDS

ROOT = Path(__file__).resolve().parents[2]
CKPT = ROOT / "ml" / "checkpoints"
OUT = ROOT / "ml" / "eval" / "thesis_exports"
OUT.mkdir(parents=True, exist_ok=True)


def _avg(rows: list[dict], model: str, field: str):
    values = [row[field] for row in rows if row.get("model") == model and row.get(field) is not None]
    return round(sum(values) / len(values), 4) if values else None


def main() -> None:
    ablation = CKPT / "ablation_metrics.json"
    rows = json.loads(ablation.read_text(encoding="utf-8")) if ablation.exists() else []

    if rows:
        (OUT / "ablation_metrics.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")
        with (OUT / "ablation_metrics.csv").open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDS)
            writer.writeheader()
            writer.writerows(rows)

    proposal = "attention" if any(r.get("model") == "attention" for r in rows) else None
    generalization = [
        {
            "train": "UK-DALE house 1",
            "test": "UK-DALE house 1 (holdout)",
            "model": proposal or "n/a",
            "mae": _avg(rows, proposal, "mae") if proposal else None,
            "f1": _avg(rows, proposal, "state_f1") if proposal else None,
            "note": "same-house holdout",
        },
        {
            "train": "UK-DALE house 1",
            "test": "UK-DALE house 2 (cross-house)",
            "model": proposal or "n/a",
            "mae": None,
            "f1": None,
            "note": "run preprocess.ukdale --house 2 and evaluate the same checkpoints",
        },
    ]
    (OUT / "generalization.json").write_text(
        json.dumps(generalization, indent=2), encoding="utf-8"
    )
    with (OUT / "generalization.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=["train", "test", "model", "mae", "f1", "note"]
        )
        writer.writeheader()
        writer.writerows(generalization)

    (OUT / "README.md").write_text(
        "# Thesis exports\n\n"
        "- `ablation_metrics.csv`: baseline -> dilated -> attention on the test split\n"
        "- `generalization.csv`: same-house holdout, plus a cross-house slot\n"
        "Generated from real evaluation results; no placeholder scores.\n",
        encoding="utf-8",
    )
    print(f"Wrote exports under {OUT}")


if __name__ == "__main__":
    main()
