"""Train a single appliance Seq2Point model."""

from __future__ import annotations

import argparse
import json
import os
import random
from pathlib import Path

import numpy as np
import torch
from torch.utils.data import DataLoader
from tqdm import tqdm

from models.seq2point import WeightedHuberLoss, WeightedMSELoss, build_model
from preprocess.config import ON_THRESHOLDS, PROCESSED_DIR, ROOT, WINDOW_SIZE
from train.dataset import WindowDataset
from train.metrics import evaluate_all

CKPT_DIR = ROOT / "ml" / "checkpoints"


def seed_everything(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


def resolve_file(manifest: dict, appliance: str, split: str) -> Path:
    rel = manifest["files"][appliance][split]
    # stored relative to NILM root
    p = ROOT / rel
    if not p.exists():
        p = PROCESSED_DIR / Path(rel).name
    return p


def _predict(
    model: torch.nn.Module,
    loader: DataLoader,
    device: torch.device,
    stats: dict,
    criterion: torch.nn.Module | None = None,
):
    model.eval()
    preds, trues, losses = [], [], []
    with torch.no_grad():
        for x, y in loader:
            x_dev, y_dev = x.to(device), y.to(device)
            output = model(x_dev)
            if criterion is not None:
                losses.append(float(criterion(output, y_dev).item()))
            preds.append(output.cpu().numpy())
            trues.append(y.numpy())
    y_pred = np.concatenate(preds) * stats["y_std"] + stats["y_mean"]
    y_true = np.concatenate(trues) * stats["y_std"] + stats["y_mean"]
    val_loss = float(np.mean(losses)) if losses else None
    return y_true, np.clip(y_pred, 0.0, None), val_loss


def train(
    appliance: str,
    model_name: str = "baseline",
    epochs: int = 5,
    batch_size: int = 128,
    lr: float = 1e-4,
    seed: int = 42,
    use_weighted_huber: bool = False,
    device_name: str | None = None,
    num_workers: int = 0,
    run_name: str | None = None,
    loss_name: str | None = None,
    pos_weight: float = 10.0,
) -> dict:
    seed_everything(seed)
    manifest = json.loads((PROCESSED_DIR / "dataset_manifest.json").read_text(encoding="utf-8"))
    if appliance not in manifest["files"]:
        raise SystemExit(f"{appliance} missing from dataset manifest")

    loss_name = loss_name or ("weighted_huber" if use_weighted_huber else "mse")
    run_name = run_name or f"{appliance}_{model_name}"
    train_ds = WindowDataset(resolve_file(manifest, appliance, "train"))
    val_ds = WindowDataset(resolve_file(manifest, appliance, "val"))
    train_loader = DataLoader(
        train_ds, batch_size=batch_size, shuffle=True, num_workers=num_workers
    )
    val_loader = DataLoader(val_ds, batch_size=batch_size * 2, shuffle=False)

    if device_name:
        device = torch.device(device_name)
    else:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = build_model(model_name, WINDOW_SIZE).to(device)
    opt = torch.optim.Adam(model.parameters(), lr=lr)
    if loss_name == "weighted_mse":
        criterion = WeightedMSELoss(pos_weight=pos_weight)
    elif use_weighted_huber:
        criterion = WeightedHuberLoss(pos_weight=pos_weight)
    else:
        criterion = torch.nn.MSELoss()

    stats = manifest["stats"][appliance]
    default_threshold = float(ON_THRESHOLDS[appliance])
    best_val = float("inf")
    best_score = -1.0
    history: list[dict] = []
    ckpt_path = CKPT_DIR / f"{run_name}.pt"
    CKPT_DIR.mkdir(parents=True, exist_ok=True)

    for epoch in range(1, epochs + 1):
        model.train()
        losses = []
        for x, y in tqdm(
            train_loader,
            desc=f"{appliance}/{model_name} ep{epoch}",
            leave=False,
            disable=os.environ.get("NILM_QUIET") == "1",
        ):
            x, y = x.to(device), y.to(device)
            opt.zero_grad()
            pred = model(x)
            loss = criterion(pred, y)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 5.0)
            opt.step()
            losses.append(loss.item())

        y_true, y_pred, val_loss = _predict(model, val_loader, device, stats, criterion)
        metrics = evaluate_all(y_true, y_pred, default_threshold)
        metrics["train_loss"] = float(np.mean(losses)) if losses else float("nan")
        metrics["val_loss"] = val_loss if val_loss is not None else float("nan")
        metrics["epoch"] = epoch
        history.append({k: float(v) for k, v in metrics.items()})
        print(
            f"[{appliance}|{model_name}] epoch {epoch}: "
            f"train_loss={metrics['train_loss']:.4f} val_loss={metrics['val_loss']:.4f} "
            f"mae={metrics['mae']:.2f} sae={metrics['sae']:.3f} "
            f"state_f1={metrics['state_f1']:.3f} event_f1={metrics['event_f1']:.3f}"
        )

        # Select on validation event-F1 (the metric we report), with MAE as a
        # tie-breaker. Selecting on MAE alone favours near-zero predictions for
        # rare appliances such as the microwave.
        score = float(metrics["event_f1"])
        better = score > best_score + 1e-9 or (
            abs(score - best_score) <= 1e-9 and metrics["mae"] < best_val
        )
        if better:
            best_score = score
            best_val = float(metrics["mae"])
            torch.save(
                {
                    "model_name": model_name,
                    "appliance": appliance,
                    "run_name": run_name,
                    "loss": loss_name,
                    "state_dict": model.state_dict(),
                    "stats": stats,
                    "window_size": WINDOW_SIZE,
                    "sample_period_s": manifest.get("sample_period_s", 1),
                    "dataset": manifest.get("dataset", ""),
                    "metrics": {k: float(v) for k, v in metrics.items()},
                    "epoch": epoch,
                },
                ckpt_path,
            )

    # Threshold calibration on the validation split (fair: never uses test data).
    from eval.evaluate import calibrate_threshold

    checkpoint = torch.load(ckpt_path, map_location="cpu", weights_only=False)
    model.load_state_dict(checkpoint["state_dict"])
    y_true, y_pred, _ = _predict(model, val_loader, device, stats)
    threshold, calibrated_f1 = calibrate_threshold(y_true, y_pred, default_threshold)
    checkpoint["on_threshold"] = threshold
    checkpoint["val_event_f1"] = calibrated_f1
    torch.save(checkpoint, ckpt_path)
    print(
        f"[{appliance}|{model_name}] best val event F1={best_score:.3f}, MAE={best_val:.2f}, "
        f"threshold={threshold:.1f} W (calibrated val event F1={calibrated_f1:.3f})"
    )

    return {
        "appliance": appliance,
        "model": model_name,
        "run": run_name,
        "loss": loss_name,
        "history": history,
        "best_mae": best_val,
        "on_threshold": threshold,
        "val_event_f1": calibrated_f1,
        "checkpoint": str(ckpt_path),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--appliance", required=True)
    parser.add_argument("--model", default="baseline")
    parser.add_argument("--epochs", type=int, default=5)
    parser.add_argument("--batch-size", type=int, default=128)
    parser.add_argument("--lr", type=float, default=1e-4)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--device", default=None, help="cpu / cuda / cuda:0")
    parser.add_argument("--num-workers", type=int, default=0)
    parser.add_argument("--weighted-huber", action="store_true")
    parser.add_argument("--run-name", default=None)
    parser.add_argument("--loss-name", default=None)
    parser.add_argument("--pos-weight", type=float, default=10.0)
    args = parser.parse_args()
    train(
        args.appliance,
        args.model,
        args.epochs,
        args.batch_size,
        args.lr,
        args.seed,
        use_weighted_huber=args.weighted_huber,
        device_name=args.device,
        num_workers=args.num_workers,
        run_name=args.run_name,
        loss_name=args.loss_name,
        pos_weight=args.pos_weight,
    )


if __name__ == "__main__":
    main()
