"""Generate all data figures for the bi-weekly progress deck."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import soundfile as sf
from matplotlib.patches import FancyBboxPatch

ROOT = Path(r"C:\Users\Wizard\Desktop\ComputerScience\毕业设计\NILM")
OUT = Path(__file__).resolve().parent / "figs"
OUT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(ROOT / "ml"))

from inference.engine import InferenceEngine  # noqa: E402

TEAL = "#40BAD2"
TEAL_DARK = "#16606B"
GREEN = "#1AB39F"
ORANGE = "#FAB900"
RED = "#D5393D"
LIME = "#90BB23"
NAVY = "#14333D"
GREY = "#94A3B8"
LIGHT = "#EAF7FA"

plt.rcParams.update(
    {
        "font.family": "Corbel",
        "font.size": 12,
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

APPLIANCES = ["fridge", "kettle", "microwave", "dishwasher", "washing_machine"]
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


def load_day():
    data = np.load(ROOT / "data/processed/replay/ukdale_house1_day1.npz")
    return data


def fig_day(data) -> None:
    agg = data["aggregate"].astype(float)
    hours = np.arange(len(agg)) / 600.0  # 600 samples per hour at 6 s
    fig, (ax1, ax2) = plt.subplots(
        2, 1, figsize=(9.2, 5.0), sharex=True, gridspec_kw={"height_ratios": [1.15, 1]}
    )
    ax1.plot(hours, agg, color=NAVY, linewidth=1.4)
    ax1.fill_between(hours, agg, color=TEAL, alpha=0.18)
    ax1.set_ylabel("Whole-home\npower (W)", fontsize=13)
    ax1.set_ylim(0, max(agg.max() * 1.08, 1000))
    ax1.text(0.5, agg.max() * 0.92, "One meter measures everything", fontsize=13, color=NAVY, weight="bold")

    bottom = np.zeros(len(agg))
    step = 6
    for appliance in APPLIANCES:
        series = data[appliance].astype(float)
        ax2.fill_between(
            hours[::step],
            bottom[::step] / 1000,
            (bottom + series)[::step] / 1000,
            color=COLORS[appliance],
            alpha=0.85,
            linewidth=0,
            label=LABELS[appliance],
        )
        bottom = bottom + series
    ax2.set_ylabel("Appliance power\n(kW)", fontsize=13)
    ax2.set_xlabel("Hour of day", fontsize=13)
    ax2.set_xlim(0, 24)
    ax2.set_xticks(range(0, 25, 3))
    ax2.legend(loc="upper left", ncol=5, frameon=False, fontsize=10, bbox_to_anchor=(0, 1.22))
    ax1.set_title("")
    for ax in (ax1, ax2):
        ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(OUT / "fig_day.png", dpi=200, bbox_inches="tight")
    plt.close(fig)


def best_window(data, hours: float = 2.0) -> int:
    n = int(hours * 600)
    score = None
    for start in range(0, len(data["aggregate"]) - n, 60):
        kettle = np.sum(data["kettle"][start : start + n] > 500)
        microwave = np.sum(data["microwave"][start : start + n] > 200)
        dishwasher = np.sum(data["dishwasher"][start : start + n] > 100)
        value = kettle + microwave + dishwasher
        if score is None or value > score:
            score = value
            best = start
    return best


def fig_disagg(data) -> None:
    start = best_window(data)
    n = 1200
    agg = data["aggregate"][start : start + n].astype(np.float32)
    engine = InferenceEngine(ROOT / "ml/checkpoints")
    series = engine.disaggregate_series(agg, stride=4)
    minutes = np.arange(0, n, 4) * 6 / 60.0
    mains = agg[::4] / 1000.0

    fig, ax = plt.subplots(figsize=(9.2, 4.7))
    ax.plot(minutes, mains, color=NAVY, linewidth=2.6, label="Measured mains")
    for appliance in APPLIANCES:
        values = series.get(appliance)
        if values is None:
            continue
        ax.plot(
            minutes,
            values[::4] / 1000.0,
            color=COLORS[appliance],
            linewidth=2.0,
            label=LABELS[appliance],
        )
    ax.set_xlabel("Minutes within a two-hour window", fontsize=13)
    ax.set_ylabel("Power (kW)", fontsize=13)
    ax.set_xlim(0, minutes[-1])
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(loc="upper left", ncol=3, frameon=False, fontsize=10, bbox_to_anchor=(0, 1.18))

    peak_idx = int(np.argmax(series["kettle"]))
    ax.annotate(
        "Kettle switch-on",
        xy=(minutes[peak_idx // 4], series["kettle"][peak_idx] / 1000),
        xytext=(minutes[peak_idx // 4] + 10, 1.05),
        fontsize=11,
        color=ORANGE,
        weight="bold",
        arrowprops={"arrowstyle": "-", "color": ORANGE, "lw": 1.4},
    )
    fig.tight_layout()
    fig.savefig(OUT / "fig_disagg.png", dpi=200, bbox_inches="tight")
    plt.close(fig)


def fig_metrics() -> None:
    rows = json.loads((ROOT / "ml/checkpoints/ablation_metrics.json").read_text(encoding="utf-8"))
    order = APPLIANCES + ["__mean__"]
    fig, ax = plt.subplots(figsize=(9.0, 4.6))
    y = np.arange(len(order))
    width = 0.36
    attention = []
    baseline = []
    for appliance in order:
        if appliance == "__mean__":
            a = np.mean([r["event_f1"] for r in rows if r["model"] == "attention"])
            b = np.mean([r["event_f1"] for r in rows if r["model"] == "baseline"])
        else:
            a = next(r["event_f1"] for r in rows if r["appliance"] == appliance and r["model"] == "attention")
            b = next(r["event_f1"] for r in rows if r["appliance"] == appliance and r["model"] == "baseline")
        attention.append(a)
        baseline.append(b)

    ax.barh(y + width / 2, attention, height=width, color=GREEN, label="Attention (proposed)")
    ax.barh(y - width / 2, baseline, height=width, color=GREY, label="Baseline CNN")
    for idx, (a, b) in enumerate(zip(attention, baseline)):
        ax.text(a + 0.01, idx + width / 2, f"{a:.2f}", va="center", fontsize=9, color=TEAL_DARK)
        ax.text(b + 0.01, idx - width / 2, f"{b:.2f}", va="center", fontsize=9, color="#64748B")
    ax.set_yticks(y)
    ax.set_yticklabels([LABELS.get(a, "Average") for a in order], fontsize=11)
    ax.invert_yaxis()
    ax.set_xlim(0, 1.0)
    ax.set_xlabel("Event-level F1 (higher is better)", fontsize=12)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(
        loc="lower right",
        bbox_to_anchor=(1.0, 1.02),
        ncol=2,
        frameon=False,
        fontsize=10,
    )
    fig.tight_layout()
    fig.savefig(OUT / "fig_metrics.png", dpi=200, bbox_inches="tight")
    plt.close(fig)


def fig_training() -> None:
    runs = json.loads((ROOT / "ml/checkpoints/training_runs.json").read_text(encoding="utf-8"))
    attention = [r for r in runs if r["model"] == "attention"]
    epochs = [1, 2, 3]
    loss = [np.mean([r["history"][i]["train_loss"] for r in attention]) for i in range(3)]
    event_f1 = [np.mean([r["history"][i]["event_f1"] for r in attention]) for i in range(3)]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.2, 3.7))
    ax1.plot(epochs, loss, marker="o", color=TEAL, linewidth=2.5)
    ax1.set_title("Training loss", fontsize=13, color=NAVY, weight="bold")
    ax1.set_xlabel("Epoch", fontsize=11)
    ax1.set_xticks(epochs)
    ax1.set_ylim(0, max(loss) * 1.15)
    for x, y in zip(epochs, loss):
        ax1.text(x, y + max(loss) * 0.04, f"{y:.2f}", ha="center", fontsize=10, color=TEAL_DARK)

    ax2.plot(epochs, event_f1, marker="o", color=ORANGE, linewidth=2.5)
    ax2.set_title("Validation event F1", fontsize=13, color=NAVY, weight="bold")
    ax2.set_xlabel("Epoch", fontsize=11)
    ax2.set_xticks(epochs)
    ax2.set_ylim(0, 1.0)
    for x, y in zip(epochs, event_f1):
        ax2.text(x, y + 0.03, f"{y:.2f}", ha="center", fontsize=10, color="#925B00")
    for ax in (ax1, ax2):
        ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(OUT / "fig_training.png", dpi=200, bbox_inches="tight")
    plt.close(fig)


def fig_whited_waves() -> None:
    raw = ROOT / "data/raw/whited"
    chosen = [
        ("Kettle", next(p for p in raw.glob("Kettle_*.flac"))),
        ("Microwave", next(p for p in raw.glob("Microwave_*.flac"))),
        ("Fridge", next(p for p in raw.glob("Fridge_*.flac"))),
    ]
    fig, axes = plt.subplots(1, 3, figsize=(9.2, 2.9), sharey=True)
    for ax, (label, path) in zip(axes, chosen):
        data, sr = sf.read(str(path), always_2d=True)
        current = data[:, 1]
        peak = int(np.argmax(np.abs(current)))
        half = int(0.025 * sr)
        segment = current[max(peak - half, 0) : peak + half]
        segment = segment / (np.max(np.abs(segment)) + 1e-9)
        ms = np.arange(len(segment)) / sr * 1000 - 25
        ax.plot(ms, segment, color=TEAL_DARK if label == "Fridge" else ORANGE, linewidth=1.6)
        ax.axvline(0, color="#CBD5E1", linewidth=1, linestyle="--")
        ax.set_title(label, fontsize=13, color=NAVY, weight="bold")
        ax.set_xlabel("ms around switch-on", fontsize=10)
        ax.spines[["top", "right"]].set_visible(False)
    axes[0].set_ylabel("Current (normalised)", fontsize=11)
    fig.tight_layout()
    fig.savefig(OUT / "fig_whited_waves.png", dpi=200, bbox_inches="tight")
    plt.close(fig)


def fig_whited_confusion() -> None:
    metrics = json.loads((ROOT / "ml/checkpoints/whited_metrics.json").read_text(encoding="utf-8"))
    pairs = metrics["confusion_top"][:6]
    labels = [f"{p['true']} -> {p['predicted']}" for p in pairs][::-1]
    counts = [p["count"] for p in pairs][::-1]
    fig, ax = plt.subplots(figsize=(9.0, 3.4))
    ax.barh(labels, counts, color=RED, alpha=0.85, height=0.6)
    for idx, value in enumerate(counts):
        ax.text(value + 0.1, idx, str(value), va="center", fontsize=10, color="#7F1D1D")
    ax.set_xlabel("Misclassified transients", fontsize=11)
    ax.set_xlim(0, max(counts) * 1.18)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(OUT / "fig_whited_confusion.png", dpi=200, bbox_inches="tight")
    plt.close(fig)


def fig_spark(data) -> None:
    agg = data["aggregate"].astype(float)
    x = np.arange(len(agg))
    fig, ax = plt.subplots(figsize=(3.8, 1.05))
    ax.plot(x, agg, color=NAVY, linewidth=0.9)
    ax.fill_between(x, agg, color=TEAL, alpha=0.25)
    ax.set_axis_off()
    fig.subplots_adjust(0, 0, 1, 1)
    fig.savefig(OUT / "fig_spark.png", dpi=220, transparent=True)
    plt.close(fig)


def main() -> None:
    data = load_day()
    fig_day(data)
    fig_disagg(data)
    fig_metrics()
    fig_training()
    fig_whited_waves()
    fig_whited_confusion()
    fig_spark(data)
    print("figures written to", OUT)


if __name__ == "__main__":
    main()
