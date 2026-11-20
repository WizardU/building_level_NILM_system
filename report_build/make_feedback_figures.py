"""Figures requested by the professor: class imbalance, threshold-F1, failure case."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch

ROOT = Path(r"C:\Users\Wizard\Desktop\ComputerScience\毕业设计\NILM")
OUT = Path(__file__).resolve().parent / "figs"
sys.path.insert(0, str(ROOT / "ml"))

TEAL = "#40BAD2"
TEAL_DARK = "#16606B"
GREEN = "#1AB39F"
ORANGE = "#EE7008"
RED = "#D5393D"
NAVY = "#14333D"
GREY = "#94A3B8"
BODY = "#475569"

plt.rcParams.update(
    {
        "font.family": "Corbel",
        "font.size": 11,
        "axes.edgecolor": "#CBD5E1",
        "axes.labelcolor": "#475569",
        "xtick.color": "#64748B",
        "ytick.color": "#64748B",
        "axes.grid": True,
        "grid.color": "#E2E8F0",
        "grid.linewidth": 0.8,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
    }
)

APPS = ["fridge", "kettle", "microwave", "dishwasher", "washing_machine"]
LABELS = {
    "fridge": "Fridge",
    "kettle": "Kettle",
    "microwave": "Microwave",
    "dishwasher": "Dishwasher",
    "washing_machine": "Washing machine",
}
COLORS = {
    "fridge": "#2E86AB",
    "kettle": "#EE7008",
    "microwave": "#D5393D",
    "dishwasher": "#90BB23",
    "washing_machine": "#7C5CBF",
}
ON_PCT = {
    "fridge": 42.47,
    "kettle": 0.55,
    "microwave": 0.39,
    "dishwasher": 2.17,
    "washing_machine": 4.19,
}
ON_HOURS = {
    "fridge": 1844.8,
    "kettle": 23.9,
    "microwave": 17.0,
    "dishwasher": 94.2,
    "washing_machine": 181.8,
}
POS_TEST = {
    "fridge": 6067,
    "kettle": 61,
    "microwave": 34,
    "dishwasher": 272,
    "washing_machine": 503,
}
POS_TRAIN = {
    "fridge": 25204,
    "kettle": 349,
    "microwave": 253,
    "dishwasher": 1380,
    "washing_machine": 2594,
}


def fig_imbalance() -> None:
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.4, 3.6))
    y = np.arange(len(APPS))

    values = [ON_PCT[a] for a in APPS]
    ax1.barh(y, values, color=[COLORS[a] for a in APPS], height=0.62)
    ax1.set_xscale("log")
    ax1.set_xlim(0.2, 100)
    ax1.set_yticks(y)
    ax1.set_yticklabels([LABELS[a] for a in APPS], fontsize=11)
    ax1.invert_yaxis()
    ax1.set_xlabel("Share of time ON (%, log scale)", fontsize=11)
    ax1.set_title("How often is each appliance ON?", fontsize=12, color=NAVY, weight="bold")
    for index, value in enumerate(values):
        ax1.text(value * 1.12, index, f"{value:.2f}%", va="center", fontsize=9.5, color=TEAL_DARK)
    ax1.spines[["top", "right"]].set_visible(False)

    test = [POS_TEST[a] for a in APPS]
    train = [POS_TRAIN[a] for a in APPS]
    height = 0.34
    ax2.barh(y - height / 2, train, height=height, color="#CBD5E1", label="Train")
    ax2.barh(y + height / 2, test, height=height, color=TEAL_DARK, label="Test")
    ax2.set_xscale("log")
    ax2.set_xlim(20, 40000)
    ax2.set_yticks(y)
    ax2.set_yticklabels([])
    ax2.invert_yaxis()
    ax2.set_xlabel("Positive windows (log scale)", fontsize=11)
    ax2.set_title("Training / test positive windows", fontsize=12, color=NAVY, weight="bold")
    for index, value in enumerate(test):
        ax2.text(value * 1.12, index + height / 2, str(value), va="center", fontsize=9, color=TEAL_DARK)
    for index, value in enumerate(train):
        ax2.text(value * 1.12, index - height / 2, str(value), va="center", fontsize=8.5, color="#64748B")
    ax2.legend(loc="lower right", frameon=False, fontsize=9)
    ax2.spines[["top", "right"]].set_visible(False)

    fig.tight_layout()
    fig.savefig(OUT / "fig_imbalance.png", dpi=220, bbox_inches="tight")
    plt.close(fig)


def fig_training_all() -> None:
    history_path = ROOT / "ml/checkpoints/training_runs_mse.json"
    if not history_path.exists():
        history_path = ROOT / "ml/checkpoints/training_runs.json"
    runs = json.loads(history_path.read_text(encoding="utf-8"))
    max_epoch = max(len(r["history"]) for r in runs)
    ticks = sorted({1, max(1, max_epoch // 4), max(1, max_epoch // 2), max(1, 3 * max_epoch // 4), max_epoch})
    fig, axes = plt.subplots(2, 3, figsize=(9.8, 5.0), sharex=True)
    axes = axes.ravel()
    for ax, appliance in zip(axes[:5], APPS):
        run = next(r for r in runs if r["appliance"] == appliance and r["model"] == "attention")
        epochs = [h["epoch"] for h in run["history"]]
        ax.plot(epochs, [h["train_loss"] for h in run["history"]], color=TEAL, linewidth=2.0, label="Train")
        ax.plot(epochs, [h["val_loss"] for h in run["history"]], color=ORANGE, linewidth=2.0, label="Validation")
        ax.set_title(LABELS[appliance], fontsize=11.5, color=NAVY, weight="bold")
        ax.set_xticks(ticks)
        ax.spines[["top", "right"]].set_visible(False)
        ax.tick_params(labelsize=9)
    axes[0].set_ylabel("Loss", fontsize=10)
    axes[3].set_ylabel("Loss", fontsize=10)
    axes[0].legend(loc="upper right", frameon=False, fontsize=8.5)

    ax = axes[5]
    for model_name, color, style in [("attention", GREEN, "-"), ("baseline", GREY, "--")]:
        runs_model = [r for r in runs if r["model"] == model_name]
        if not runs_model:
            continue
        length = min(len(r["history"]) for r in runs_model)
        mean_f1 = [
            np.mean([r["history"][i]["event_f1"] for r in runs_model]) for i in range(length)
        ]
        ax.plot(range(1, length + 1), mean_f1, color=color, linestyle=style, linewidth=2.0, label=model_name)
    ax.set_title("Validation event F1 (default)", fontsize=11.5, color=NAVY, weight="bold")
    ax.set_ylim(0, 1)
    ax.set_xticks(ticks)
    ax.set_xlabel("Epoch", fontsize=9.5)
    ax.legend(frameon=False, fontsize=8.5, loc="lower right")
    ax.spines[["top", "right"]].set_visible(False)
    ax.tick_params(labelsize=9)

    fig.tight_layout()
    fig.savefig(OUT / "fig_training_all.png", dpi=220, bbox_inches="tight")
    plt.close(fig)


def fig_threshold_curves() -> None:
    import torch
    from eval.evaluate import predict_split
    from train.metrics import event_scores

    fig, axes = plt.subplots(2, 3, figsize=(9.6, 4.9))
    axes = axes.ravel()
    for ax, appliance in zip(axes[:5], APPS):
        ckpt = torch.load(
            ROOT / f"ml/checkpoints/{appliance}_attention_mse.pt",
            map_location="cpu",
            weights_only=False,
        )
        y_true, y_pred = predict_split(ckpt, "test")
        upper = max(float(np.quantile(y_pred, 0.999)), 1.0)
        thresholds = np.linspace(0.0, upper, 80)
        f1 = np.array([event_scores(y_true, y_pred, float(t))["f1"] for t in thresholds])
        best = int(np.argmax(f1))
        ax.plot(thresholds, f1, color=GREEN, linewidth=2.2)
        ax.scatter([thresholds[best]], [f1[best]], color=ORANGE, zorder=3, s=28)
        chosen = float(ckpt.get("on_threshold", 0))
        ax.axvline(chosen, color=GREY, linestyle="--", linewidth=1.0)
        ax.set_title(f"{LABELS[appliance]}  (max {f1[best]:.2f})", fontsize=11, color=NAVY, weight="bold")
        ax.set_ylim(0, 1)
        ax.set_xlim(0, upper)
        ax.tick_params(labelsize=8.5)
        ax.spines[["top", "right"]].set_visible(False)
    axes[5].axis("off")
    axes[5].text(
        0.02,
        0.7,
        "Even at the best threshold,\nmicrowave event F1 stays low.\nThe problem is recall, not\nthe operating point.",
        fontsize=10.5,
        color=BODY,
        va="top",
    )
    for ax in axes[:5]:
        ax.set_xlabel("ON threshold (W)", fontsize=9)
    axes[0].set_ylabel("Event F1", fontsize=10)
    axes[3].set_ylabel("Event F1", fontsize=10)
    fig.tight_layout()
    fig.savefig(OUT / "fig_threshold.png", dpi=220, bbox_inches="tight")
    plt.close(fig)


def fig_failure() -> None:
    sys.path.insert(0, str(ROOT / "ml"))
    from inference.engine import InferenceEngine

    data = np.load(ROOT / "data/processed/replay/ukdale_house1_day1.npz")
    n = 1200
    start = 5160
    agg = data["aggregate"][start : start + n].astype(np.float32)
    minutes = np.arange(0, n, 4) * 6 / 60.0

    engine = InferenceEngine(ROOT / "ml/checkpoints")
    pred = engine.disaggregate_series(agg, stride=4)

    fig, (ax1, ax2) = plt.subplots(
        2, 1, figsize=(9.4, 4.5), sharex=True, gridspec_kw={"height_ratios": [1, 1.25]}
    )
    for ax in (ax1, ax2):
        ax.axvspan(0, 20, color="#FDE8E8", alpha=0.7, zorder=0)
        ax.axvspan(90, 120, color="#FDE8E8", alpha=0.7, zorder=0)
        ax.spines[["top", "right"]].set_visible(False)

    ax1.plot(minutes, agg[::4] / 1000.0, color=NAVY, linewidth=2.4)
    ax1.set_ylabel("Whole-home\npower (kW)", fontsize=10.5)
    ax1.set_ylim(0, 3.0)
    ax1.text(2, 2.55, "microwave spike", fontsize=9.5, color=RED, weight="bold")
    ax1.text(92, 2.55, "dishwasher cycle", fontsize=9.5, color=RED, weight="bold")

    truth_dw = data["dishwasher"][start : start + n].astype(float)
    truth_mw = data["microwave"][start : start + n].astype(float)
    dw_true = truth_dw[900:].mean() / 1000.0
    dw_pred = pred["dishwasher"][225:].mean() / 1000.0
    ax2.plot(minutes, truth_dw[::4] / 1000.0, color="#90BB23", linewidth=2.2, label="Dishwasher truth")
    ax2.plot(minutes, pred["dishwasher"][::4] / 1000.0, color="#90BB23", linewidth=1.8, linestyle="--", label="Dishwasher model")
    ax2.plot(minutes, truth_mw[::4] / 1000.0, color=ORANGE, linewidth=2.0, label="Microwave truth")
    ax2.plot(minutes, pred["microwave"][::4] / 1000.0, color=ORANGE, linewidth=1.5, linestyle="--", label="Microwave model")
    ax2.set_ylabel("Appliance\npower (kW)", fontsize=10.5)
    ax2.set_xlabel("Minutes within the two-hour window", fontsize=10.5)
    ax2.set_xlim(0, 120)
    ax2.set_ylim(0, 2.6)
    ax2.legend(loc="upper left", frameon=False, ncol=2, fontsize=8.5, bbox_to_anchor=(0, 1.02))
    ax2.annotate(
        f"true {dw_true:.1f} kW\nmodel {dw_pred:.1f} kW",
        xy=(104, max(dw_true * 0.92, 0.3)),
        xytext=(72, 1.75),
        fontsize=9.5,
        color=RED,
        weight="bold",
        arrowprops={"arrowstyle": "-", "color": RED, "lw": 1.2},
    )
    fig.tight_layout()
    fig.savefig(OUT / "fig_failure.png", dpi=220, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    fig_imbalance()
    fig_training_all()
    fig_threshold_curves()
    fig_failure()
    print("feedback figures written to", OUT)


if __name__ == "__main__":
    main()
