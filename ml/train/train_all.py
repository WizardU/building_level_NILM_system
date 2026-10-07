"""Train all appliances for one or more model variants; write ablation CSV."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from preprocess.config import APPLIANCES, PROCESSED_DIR, ROOT
from train.train_one import train

CKPT_DIR = ROOT / "ml" / "checkpoints"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument(
        "--models",
        nargs="+",
        default=["baseline", "dilated", "attention"],
        help="Model variants for ablation",
    )
    parser.add_argument("--appliances", nargs="+", default=None)
    parser.add_argument("--weighted-huber", action="store_true")
    args = parser.parse_args()

    if not (PROCESSED_DIR / "dataset_manifest.json").exists():
        raise SystemExit("Missing processed data. Run: python -m preprocess.generate_synthetic")

    apps = args.appliances or APPLIANCES
    rows = []
    for model_name in args.models:
        use_huber = args.weighted_huber or model_name == "attention"
        for app in apps:
            result = train(
                app,
                model_name=model_name,
                epochs=args.epochs,
                use_weighted_huber=use_huber,
            )
            last = result["history"][-1]
            rows.append(
                {
                    "appliance": app,
                    "model": model_name,
                    "mae": last["mae"],
                    "sae": last["sae"],
                    "f1": last["f1"],
                    "accuracy": last["accuracy"],
                }
            )

    CKPT_DIR.mkdir(parents=True, exist_ok=True)
    csv_path = CKPT_DIR / "ablation_metrics.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["appliance", "model", "mae", "sae", "f1", "accuracy"])
        w.writeheader()
        w.writerows(rows)
    (CKPT_DIR / "ablation_metrics.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")
    print(f"Wrote {csv_path}")


if __name__ == "__main__":
    main()
