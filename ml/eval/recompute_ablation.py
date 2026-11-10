"""Recompute the ablation CSV from saved checkpoints on the test split."""

from __future__ import annotations

import csv
import json

from eval.evaluate import FIELDS, evaluate_checkpoint
from preprocess.config import ROOT

CKPT = ROOT / "ml" / "checkpoints"


def main() -> None:
    rows = []
    for pt in sorted(CKPT.glob("*.pt")):
        try:
            row = evaluate_checkpoint(pt, split="test")
        except FileNotFoundError as exc:
            print(f"skip {pt.name}: {exc}")
            continue
        rows.append(row)
        print(
            f"{row['appliance']:16s} {row['model']:10s} "
            f"MAE={row['mae']:8.2f} SAE={row['sae']:.3f} "
            f"state_F1={row['state_f1']:.3f} event_F1={row['event_f1']:.3f}"
        )

    with (CKPT / "ablation_metrics.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    (CKPT / "ablation_metrics.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")
    print(f"wrote {CKPT / 'ablation_metrics.csv'} ({len(rows)} rows)")


if __name__ == "__main__":
    main()
