"""Train all appliances for one or more model variants; write ablation tables."""

from __future__ import annotations

import argparse
import csv
import json

from preprocess.config import APPLIANCES, PROCESSED_DIR, ROOT
from train.train_one import train

CKPT_DIR = ROOT / "ml" / "checkpoints"
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
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--device", default=None)
    parser.add_argument("--weighted-huber", action="store_true")
    parser.add_argument("--skip-train", action="store_true", help="Only re-evaluate checkpoints")
    args = parser.parse_args()

    if not (PROCESSED_DIR / "dataset_manifest.json").exists():
        raise SystemExit(
            "Missing processed data. Run: python -m preprocess.ukdale --h5 data/raw/ukdale.h5"
        )

    apps = args.appliances or APPLIANCES
    trained = []
    if not args.skip_train:
        for model_name in args.models:
            use_huber = args.weighted_huber or model_name == "attention"
            for app in apps:
                result = train(
                    app,
                    model_name=model_name,
                    epochs=args.epochs,
                    seed=args.seed,
                    use_weighted_huber=use_huber,
                    device_name=args.device,
                )
                trained.append(result)

    from eval.evaluate import evaluate_checkpoint

    rows = []
    for pt in sorted(CKPT_DIR.glob("*.pt")):
        try:
            rows.append(evaluate_checkpoint(pt, split="test"))
        except FileNotFoundError:
            continue

    CKPT_DIR.mkdir(parents=True, exist_ok=True)
    csv_path = CKPT_DIR / "ablation_metrics.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    (CKPT_DIR / "ablation_metrics.json").write_text(
        json.dumps(rows, indent=2), encoding="utf-8"
    )

    summary = {f"{r['appliance']}/{r['model']}": r for r in rows}
    print(json.dumps(summary, indent=2)[:4000])
    print(f"Wrote {csv_path} ({len(rows)} rows)")
    if trained:
        (CKPT_DIR / "training_runs.json").write_text(
            json.dumps(trained, indent=2), encoding="utf-8"
        )


if __name__ == "__main__":
    main()
