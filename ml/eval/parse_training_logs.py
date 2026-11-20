"""Parse training logs into a JSON history for MSE variants."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(r"C:\Users\Wizard\Desktop\ComputerScience\毕业设计\NILM")
OUT = ROOT / "ml" / "checkpoints" / "training_runs_mse.json"
LOGS = [
    ("attention", "mse", ROOT / "report_build/train_attention_mse.log"),
    ("baseline", "mse", ROOT / "report_build/train_loss_mse.log"),
    ("dilated", "mse", ROOT / "report_build/train_dilated_mse.log"),
]
PATTERN = re.compile(
    r"^\[(?P<app>[^|]+)\|(?P<model>[^\]]+)\] epoch (?P<epoch>\d+): "
    r"train_loss=(?P<train>[0-9.]+) val_loss=(?P<val>[0-9.]+) "
    r"mae=(?P<mae>[0-9.]+) sae=(?P<sae>[0-9.]+) "
    r"state_f1=(?P<state>[0-9.]+) event_f1=(?P<event>[0-9.]+)"
)


def main() -> None:
    runs: dict[tuple[str, str], dict] = {}
    for model, loss, path in LOGS:
        if not path.exists():
            continue
        raw = path.read_bytes()
        if raw.startswith((b"\xff\xfe", b"\xfe\xff")):
            text = raw.decode("utf-16", errors="ignore")
        else:
            text = raw.decode("utf-8", errors="ignore")
        for line in text.splitlines():
            match = PATTERN.match(line.strip())
            if not match:
                continue
            app = match["app"]
            key = (app, model)
            run = runs.setdefault(
                key,
                {"appliance": app, "model": model, "loss": loss, "history": []},
            )
            run["history"].append(
                {
                    "epoch": float(match["epoch"]),
                    "train_loss": float(match["train"]),
                    "val_loss": float(match["val"]),
                    "mae": float(match["mae"]),
                    "sae": float(match["sae"]),
                    "state_f1": float(match["state"]),
                    "event_f1": float(match["event"]),
                }
            )
    output = list(runs.values())
    OUT.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print("wrote", OUT, "runs", len(output))


if __name__ == "__main__":
    main()
