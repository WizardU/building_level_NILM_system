"""Summarise the 2x2 architecture x loss ablation."""

from __future__ import annotations

import json

from preprocess.config import APPLIANCES, ROOT

CKPT_DIR = ROOT / "ml" / "checkpoints"


def pick(rows, appliance, model, loss):
    return next(
        r
        for r in rows
        if r["appliance"] == appliance
        and r["model"] == model
        and r.get("loss", "weighted_huber") == loss
    )


def main() -> None:
    rows = json.loads((CKPT_DIR / "ablation_metrics.json").read_text(encoding="utf-8"))
    output = []
    for appliance in APPLIANCES:
        item = {"appliance": appliance}
        for model in ("baseline", "attention"):
            for loss in ("mse", "weighted_huber"):
                row = pick(rows, appliance, model, loss)
                item[f"{model}_{loss}"] = {
                    key: row[key] for key in ("mae", "rmse", "sae", "state_f1", "event_f1")
                }
        output.append(item)
        print(
            f"{appliance:16s} base-MSE event={item['baseline_mse']['event_f1']:.3f} "
            f"att-MSE event={item['attention_mse']['event_f1']:.3f} "
            f"base-Huber event={item['baseline_weighted_huber']['event_f1']:.3f} "
            f"att-Huber event={item['attention_weighted_huber']['event_f1']:.3f}"
        )

    means = {}
    for model in ("baseline", "attention"):
        for loss in ("mse", "weighted_huber"):
            key = f"{model}_{loss}"
            means[key] = {
                metric: sum(item[key][metric] for item in output) / len(output)
                for metric in ("mae", "rmse", "sae", "state_f1", "event_f1")
            }
    payload = {"rows": output, "means": means}
    (CKPT_DIR / "loss_ablation.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print("means", json.dumps(means, indent=2))


if __name__ == "__main__":
    main()
