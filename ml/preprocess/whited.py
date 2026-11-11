"""WHITED appliance-identification experiment (transient features + classifier).

WHITED v1.1 stores 44.1 kHz stereo FLACs: channel 0 is voltage, channel 1 is
current. We extract time/frequency features from the current channel and train a
classifier to identify the appliance type.

Split is by **device** (filename without timestamp) so transients of the same
device never appear in both train and test.

Usage:
    python -m preprocess.whited --raw ../data/raw/whited
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import soundfile as sf
from scipy import stats
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from .config import RAW_DIR, ROOT

FEATURE_NAMES = [
    "rms",
    "peak",
    "crest",
    "zcr",
    "skew",
    "kurtosis",
    "centroid",
    "bandwidth",
    "rolloff85",
    "flatness",
    "dominant_hz",
    "harmonics_ratio",
    "inrush_ratio",
    "steady_cv",
    "band_0_100",
    "band_100_500",
    "band_500_2k",
    "band_2k_8k",
    "band_8k_22k",
]

BANDS = [(0, 100), (100, 500), (500, 2000), (2000, 8000), (8000, 22050)]
EPS = 1e-12


def parse_name(path: Path) -> tuple[str, str]:
    """Return (label, device_group) from a WHITED filename."""
    parts = path.stem.split("_")
    label = parts[0]
    group = "_".join(parts[:-1])  # drop timestamp
    return label, group


def extract_features(current: np.ndarray, samplerate: int) -> np.ndarray:
    x = np.asarray(current, dtype=np.float64)
    x = x - x.mean()
    n = len(x)
    rms = float(np.sqrt(np.mean(x**2)))
    peak = float(np.max(np.abs(x)))
    crest = peak / (rms + EPS)
    zcr = float(np.mean(np.diff(np.signbit(x)) != 0))
    skew = float(stats.skew(x))
    kurt = float(stats.kurtosis(x))

    spectrum = np.abs(np.fft.rfft(x)) ** 2
    freqs = np.fft.rfftfreq(n, 1.0 / samplerate)
    total = float(spectrum.sum()) + EPS
    centroid = float((freqs * spectrum).sum() / total)
    bandwidth = float(np.sqrt(((freqs - centroid) ** 2 * spectrum).sum() / total))
    cumulative = np.cumsum(spectrum)
    rolloff = float(freqs[int(np.searchsorted(cumulative, 0.85 * cumulative[-1]))])
    flatness = float(np.exp(np.mean(np.log(spectrum + EPS))) / (np.mean(spectrum) + EPS))
    dominant = float(freqs[int(np.argmax(spectrum[1:])) + 1])

    # Energy at 50 Hz harmonics (mains-related) as a share of total energy.
    harmonics = 0.0
    for k in range(1, 21):
        target = 50.0 * k
        if target >= freqs[-1]:
            break
        idx = int(np.argmin(np.abs(freqs - target)))
        lo, hi = max(idx - 2, 0), min(idx + 3, len(spectrum))
        harmonics += float(spectrum[lo:hi].sum())
    harmonics_ratio = harmonics / total

    # Inrush: early RMS versus the steady tail.
    early = x[: max(int(0.15 * samplerate), 1)]
    tail = x[-samplerate:] if n > samplerate else x
    inrush_ratio = float(np.sqrt(np.mean(early**2)) / (np.sqrt(np.mean(tail**2)) + EPS))
    steady_cv = float(np.std(tail) / (np.mean(np.abs(tail)) + EPS))

    band_ratios = []
    for lo, hi in BANDS:
        mask = (freqs >= lo) & (freqs < hi)
        band_ratios.append(float(spectrum[mask].sum() / total))

    return np.array(
        [
            rms,
            peak,
            crest,
            zcr,
            skew,
            kurt,
            centroid,
            bandwidth,
            rolloff,
            flatness,
            dominant,
            harmonics_ratio,
            inrush_ratio,
            steady_cv,
            *band_ratios,
        ],
        dtype=np.float64,
    )


def load_dataset(raw_dir: Path) -> tuple[np.ndarray, np.ndarray, np.ndarray, dict]:
    files = sorted(raw_dir.glob("*.flac"))
    if not files:
        raise SystemExit(f"no FLAC files in {raw_dir}")
    features, labels, groups = [], [], []
    skipped = []
    for index, path in enumerate(files, start=1):
        try:
            data, samplerate = sf.read(str(path), always_2d=True)
        except Exception as exc:  # noqa: BLE001 - report and skip broken files
            skipped.append({"file": path.name, "error": str(exc)[:120]})
            continue
        if data.shape[1] < 2:
            skipped.append({"file": path.name, "error": "expected stereo voltage/current"})
            continue
        label, group = parse_name(path)
        features.append(extract_features(data[:, 1], samplerate))
        labels.append(label)
        groups.append(group)
        if index % 100 == 0:
            print(f"  features {index}/{len(files)}", flush=True)
    info = {
        "files": len(files),
        "used": len(features),
        "skipped": skipped,
        "samplerate": int(samplerate) if features else 0,
        "labels": Counter(labels),
        "devices": len(set(groups)),
        "regions": sorted({g.split("_")[-2] for g in groups if "_" in g}),
    }
    # Normalise case variants such as HairDryer/Hairdryer (same appliance type).
    counts = Counter(labels)
    canonical: dict[str, str] = {}
    for label in sorted(counts, key=lambda item: (-counts[item], item)):
        canonical.setdefault(label.lower(), label)
    labels = [canonical[label.lower()] for label in labels]
    info["labels"] = Counter(labels)
    return (
        np.vstack(features),
        np.array(labels),
        np.array(groups),
        info,
    )


def top_k_accuracy(probabilities: np.ndarray, y_true: np.ndarray, labels: np.ndarray, k: int = 3) -> float:
    top = np.argsort(probabilities, axis=1)[:, -k:]
    label_to_index = {str(label): index for index, label in enumerate(labels)}
    hits = 0
    for row, truth in enumerate(y_true):
        index = label_to_index.get(str(truth))
        hits += int(index is not None and index in top[row])
    return float(hits / len(y_true))


def split_by_device(
    labels: np.ndarray,
    groups: np.ndarray,
    seed: int = 42,
    test_ratio: float = 0.25,
) -> tuple[np.ndarray, np.ndarray, dict]:
    """Hold out whole devices, keeping at least one device per class in train.

    Classes with a single device cannot be evaluated under a device split, so
    they are train-only and reported explicitly.
    """
    rng = np.random.default_rng(seed)
    train_groups: set[str] = set()
    test_groups: set[str] = set()
    train_only_classes: list[str] = []
    for label in sorted(set(labels)):
        devices = sorted({str(g) for g, y in zip(groups, labels) if y == label})
        train_groups.add(devices[0])
        remaining = devices[1:]
        if not remaining:
            train_only_classes.append(label)
            continue
        n_test = max(1, int(round(test_ratio * len(devices))))
        n_test = min(n_test, len(remaining))
        chosen = set(rng.choice(remaining, size=n_test, replace=False).tolist())
        test_groups |= chosen
        train_groups |= set(remaining) - chosen
    train_idx = np.array([i for i, g in enumerate(groups) if str(g) in train_groups], dtype=np.int64)
    test_idx = np.array([i for i, g in enumerate(groups) if str(g) in test_groups], dtype=np.int64)
    split_info = {
        "type": "device_holdout",
        "test_ratio": test_ratio,
        "seed": seed,
        "train_devices": len(train_groups),
        "test_devices": len(test_groups),
        "classes_train_only": train_only_classes,
    }
    return train_idx, test_idx, split_info


def train(raw_dir: Path, out_dir: Path, test_size: float = 0.2, seed: int = 42) -> dict:
    print(f"Loading WHITED from {raw_dir}")
    features, labels, groups, info = load_dataset(raw_dir)
    print(f"  matrix: {features.shape}, classes: {len(info['labels'])}, devices: {info['devices']}")

    splitter = split_by_device(labels, groups, seed=seed, test_ratio=test_size)
    train_idx, test_idx, split_info = splitter
    x_train, x_test = features[train_idx], features[test_idx]
    y_train, y_test = labels[train_idx], labels[test_idx]
    print(
        f"  split: train={len(train_idx)} test={len(test_idx)} "
        f"devices={split_info['train_devices']}/{split_info['test_devices']} "
        f"train-only classes={len(split_info['classes_train_only'])}"
    )

    candidates = {
        "random_forest": RandomForestClassifier(
            n_estimators=400,
            min_samples_leaf=1,
            class_weight="balanced_subsample",
            n_jobs=1,
            random_state=seed,
        ),
        "logistic_regression": make_pipeline(
            StandardScaler(),
            LogisticRegression(max_iter=3000, class_weight="balanced"),
        ),
    }

    results = {}
    best_name, best_model, best_f1 = None, None, -1.0
    for name, model in candidates.items():
        model.fit(x_train, y_train)
        predictions = model.predict(x_test)
        probabilities = model.predict_proba(x_test)
        classes = np.asarray(model.classes_)
        accuracy = float(accuracy_score(y_test, predictions))
        macro_f1 = float(f1_score(y_test, predictions, average="macro", zero_division=0))
        weighted_f1 = float(f1_score(y_test, predictions, average="weighted", zero_division=0))
        top3 = top_k_accuracy(probabilities, y_test, classes, k=3)
        results[name] = {
            "accuracy": round(accuracy, 4),
            "macro_f1": round(macro_f1, 4),
            "weighted_f1": round(weighted_f1, 4),
            "top3_accuracy": round(top3, 4),
        }
        print(f"  {name}: acc={accuracy:.3f} macroF1={macro_f1:.3f} top3={top3:.3f}")
        if macro_f1 > best_f1:
            best_name, best_model, best_f1 = name, model, macro_f1

    predictions = best_model.predict(x_test)
    labels_in_test = sorted(set(y_test))
    report = classification_report(
        y_test,
        predictions,
        labels=labels_in_test,
        output_dict=True,
        zero_division=0,
    )
    per_class = [
        {
            "label": label,
            "support": int(report[label]["support"]),
            "precision": round(float(report[label]["precision"]), 4),
            "recall": round(float(report[label]["recall"]), 4),
            "f1": round(float(report[label]["f1-score"]), 4),
        }
        for label in labels_in_test
    ]

    matrix = confusion_matrix(y_test, predictions, labels=labels_in_test)
    confused = []
    for i, true_label in enumerate(labels_in_test):
        for j, predicted_label in enumerate(labels_in_test):
            if i != j and matrix[i, j] > 0:
                confused.append(
                    {"true": true_label, "predicted": predicted_label, "count": int(matrix[i, j])}
                )
    confused.sort(key=lambda item: item["count"], reverse=True)

    out_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(
        {"model": best_model, "features": FEATURE_NAMES, "labels": list(best_model.classes_)},
        out_dir / "whited_classifier.joblib",
    )
    np.savez_compressed(
        out_dir / "whited_features.npz",
        x=features,
        y=labels,
        groups=groups,
        train_idx=train_idx,
        test_idx=test_idx,
    )

    metrics = {
        "dataset": "WHITED v1.1",
        "source": "https://huggingface.co/datasets/maduschek/WHITED",
        "license": "CC BY 4.0",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "samples": int(features.shape[0]),
        "classes": int(len(info["labels"])),
        "devices": int(info["devices"]),
        "features": FEATURE_NAMES,
        "split": {
            **split_info,
            "train_samples": int(len(train_idx)),
            "test_samples": int(len(test_idx)),
            "classes_in_train": int(len(set(y_train))),
            "classes_in_test": int(len(labels_in_test)),
        },
        "models": results,
        "best_model": best_name,
        "per_class": per_class,
        "confusion_top": confused[:8],
        "skipped": info["skipped"],
        "class_counts": dict(sorted(info["labels"].items())),
    }
    (out_dir / "whited_metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    index = {
        "dataset": "WHITED v1.1",
        "files": info["files"],
        "used": info["used"],
        "samplerate": info["samplerate"],
        "channels": 2,
        "classes": int(len(info["labels"])),
        "devices": int(info["devices"]),
        "regions": info["regions"],
        "class_counts": dict(sorted(info["labels"].items())),
        "source": "https://huggingface.co/datasets/maduschek/WHITED",
        "license": "CC BY 4.0",
    }
    (out_dir / "whited_index.json").write_text(json.dumps(index, indent=2), encoding="utf-8")
    print(f"Wrote {out_dir / 'whited_metrics.json'}")
    return metrics


def main() -> None:
    parser = argparse.ArgumentParser(description="WHITED appliance identification experiment")
    parser.add_argument("--raw", type=Path, default=RAW_DIR / "whited")
    parser.add_argument("--out", type=Path, default=ROOT / "ml" / "checkpoints")
    parser.add_argument("--test-size", type=float, default=0.2)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    metrics = train(args.raw, args.out, args.test_size, args.seed)
    print(json.dumps({k: metrics[k] for k in ("samples", "classes", "devices", "best_model")}, indent=2))


if __name__ == "__main__":
    main()
