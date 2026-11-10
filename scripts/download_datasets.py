"""Download the real NILM datasets used by this project.

Datasets
--------
ukdale : UK-DALE (April 2017 release), NILMTK HDF5 bundle (~5.1 GB zip)
         Official host: UKERC EDC / CEDA, CC BY 4.0.
whited : WHITED v1.1 transient dataset (~1.0k FLAC files, ~230 MB)
         HuggingFace mirror (CC BY 4.0); official host is TUM.

Both downloads are resumable and verify file sizes. Run:

    python scripts/download_datasets.py --dataset all
    python scripts/download_datasets.py --dataset ukdale
    python scripts/download_datasets.py --dataset whited --workers 8

Files land in ``data/raw/`` (git-ignored). A manifest with sizes and SHA-256
digests is written next to the data so the preprocessing step can verify it.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"

UKDALE_URL = (
    "https://dap.ceda.ac.uk/edc/d1/7d78f943-f9fe-413b-af52-1816f9d968b0/"
    "data/version_0/ukdale.h5.zip"
)
UKDALE_SIZE = 5_466_002_082  # bytes, from Content-Range of the official object
UKDALE_NAME = "ukdale.h5.zip"

WHITED_REPO = "maduschek/WHITED"
WHITED_API = f"https://huggingface.co/api/datasets/{WHITED_REPO}/tree/main?recursive=false"
WHITED_BASE = f"https://huggingface.co/datasets/{WHITED_REPO}/resolve/main/"
WHITED_DIR = RAW / "whited"

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) nilm-thesis/1.0"


def human(n: float) -> str:
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if abs(n) < 1024:
            return f"{n:.1f}{unit}"
        n /= 1024
    return f"{n:.1f}PB"


def free_space_gb(path: Path) -> float:
    return shutil.disk_usage(path).free / 1024**3


class Progress:
    def __init__(self, total: int, label: str):
        self.total = total
        self.label = label
        self.start = time.time()
        self.last = 0.0

    def update(self, done: int) -> None:
        now = time.time()
        if now - self.last < 2.0 and done < self.total:
            return
        self.last = now
        elapsed = max(now - self.start, 1e-6)
        speed = done / elapsed
        pct = 100.0 * done / self.total if self.total else 0.0
        eta = (self.total - done) / speed if speed > 0 else 0
        print(
            f"\r{self.label}: {pct:5.1f}%  {human(done)}/{human(self.total)}"
            f"  {human(speed)}/s  ETA {eta/60:4.1f} min",
            end="",
            flush=True,
        )

    def done(self) -> None:
        print(flush=True)


def download_resumable(url: str, dest: Path, total: int, label: str) -> Path:
    """Download with HTTP Range resume into ``dest.part`` then rename."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    part = dest.with_suffix(dest.suffix + ".part")
    if dest.exists() and dest.stat().st_size == total:
        print(f"{label}: already complete ({human(total)})")
        return dest

    pos = part.stat().st_size if part.exists() else 0
    if pos > total:
        part.unlink()
        pos = 0
    headers = {"User-Agent": UA}
    if pos:
        headers["Range"] = f"bytes={pos}-"
        print(f"{label}: resuming at {human(pos)}")

    progress = Progress(total, label)
    attempt = 0
    while pos < total:
        attempt += 1
        try:
            req = urllib.request.Request(url, headers={**headers, "Range": f"bytes={pos}-"})
            with urllib.request.urlopen(req, timeout=120) as resp:
                if resp.status == 200 and pos:
                    # Server ignored the range: restart from scratch.
                    print(f"\n{label}: server ignores Range, restarting")
                    pos = 0
                    part.unlink(missing_ok=True)
                mode = "ab" if pos else "wb"
                with part.open(mode) as fh:
                    while True:
                        chunk = resp.read(1024 * 1024)
                        if not chunk:
                            break
                        fh.write(chunk)
                        pos += len(chunk)
                        progress.update(pos)
                        if pos >= total:
                            break
        except (urllib.error.URLError, TimeoutError, ConnectionError, OSError) as exc:
            print(f"\n{label}: network error ({exc}); retry {attempt}/20 in 5s")
            time.sleep(5)
            if attempt >= 20:
                raise SystemExit(f"{label}: too many retries") from exc
            pos = part.stat().st_size if part.exists() else 0
            headers["Range"] = f"bytes={pos}-"

    progress.done()
    if part.stat().st_size != total:
        raise SystemExit(
            f"{label}: size mismatch ({part.stat().st_size} != {total}), file left at {part}"
        )
    part.replace(dest)
    print(f"{label}: saved -> {dest}")
    return dest


def sha256_of(path: Path, chunk: int = 8 * 1024 * 1024) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        while True:
            block = fh.read(chunk)
            if not block:
                break
            h.update(block)
    return h.hexdigest()


def download_ukdale() -> dict:
    dest = RAW / UKDALE_NAME
    if free_space_gb(RAW if RAW.exists() else ROOT) < 15:
        raise SystemExit("Need at least 15 GB free for UK-DALE (zip + extracted HDF5)")
    path = download_resumable(UKDALE_URL, dest, UKDALE_SIZE, "ukdale.h5.zip")
    print("ukdale: computing sha256 (a few minutes)...", flush=True)
    digest = sha256_of(path)
    return {
        "name": "ukdale",
        "path": str(path.relative_to(ROOT)).replace("\\", "/"),
        "bytes": path.stat().st_size,
        "sha256": digest,
        "source": UKDALE_URL,
        "license": "CC BY 4.0",
        "citation": "Kelly & Knottenbelt, Sci. Data 2:150007 (2015), doi:10.1038/sdata.2015.7",
    }


def list_whited() -> list[dict]:
    with urllib.request.urlopen(
        urllib.request.Request(WHITED_API, headers={"User-Agent": UA}), timeout=60
    ) as resp:
        items = json.loads(resp.read().decode("utf-8"))
    files = []
    for it in items:
        if it.get("type") == "file" and it.get("path", "").lower().endswith(".flac"):
            files.append({"path": it["path"], "size": int(it.get("size") or 0)})
    return files


def fetch_one(item: dict, dest_dir: Path, total: int | None = None) -> dict:
    rel = item["path"]
    out = dest_dir / rel
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists() and out.stat().st_size == item["size"]:
        return {"path": rel, "bytes": out.stat().st_size, "sha256": None, "skipped": True}
    url = WHITED_BASE + urllib.parse.quote(rel, safe="/")
    tmp = out.with_suffix(out.suffix + ".part")
    last_err = None
    for attempt in range(1, 6):
        try:
            with urllib.request.urlopen(
                urllib.request.Request(url, headers={"User-Agent": UA}), timeout=120
            ) as resp:
                data = resp.read()
            if len(data) != item["size"]:
                raise ValueError(f"size {len(data)} != {item['size']}")
            tmp.write_bytes(data)
            tmp.replace(out)
            return {"path": rel, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}
        except Exception as exc:  # noqa: BLE001 - network retry loop
            last_err = exc
            time.sleep(2 * attempt)
    raise RuntimeError(f"{rel}: {last_err}")


def download_whited(workers: int = 8) -> dict:
    if free_space_gb(RAW if RAW.exists() else ROOT) < 5:
        raise SystemExit("Need at least 5 GB free for WHITED")
    RAW.mkdir(parents=True, exist_ok=True)
    files = list_whited()
    total = sum(f["size"] for f in files)
    print(f"whited: {len(files)} FLAC files, {human(total)} total")
    progress = Progress(total, "whited")
    done_bytes = 0
    entries = []
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(fetch_one, f, WHITED_DIR): f for f in files}
        for fut in as_completed(futures):
            entry = fut.result()
            entries.append(entry)
            done_bytes += entry["bytes"]
            progress.update(done_bytes)
    progress.done()
    entries.sort(key=lambda e: e["path"])
    return {
        "name": "whited",
        "path": str(WHITED_DIR.relative_to(ROOT)).replace("\\", "/"),
        "files": len(entries),
        "bytes": done_bytes,
        "source": f"https://huggingface.co/datasets/{WHITED_REPO}",
        "license": "CC BY 4.0",
        "citation": "Kahl et al., WHITED (2016), doi:10.1109/TSG.2016.2628812",
        "entries": entries,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", choices=["ukdale", "whited", "all"], default="all")
    parser.add_argument("--workers", type=int, default=8, help="parallel downloads for WHITED")
    args = parser.parse_args()

    RAW.mkdir(parents=True, exist_ok=True)
    if args.dataset in ("ukdale", "all"):
        info = download_ukdale()
        (RAW / "manifest_ukdale.json").write_text(
            json.dumps(info, indent=2, ensure_ascii=False), encoding="utf-8"
        )
    if args.dataset in ("whited", "all"):
        info = download_whited(args.workers)
        (RAW / "manifest_whited.json").write_text(
            json.dumps(info, indent=2, ensure_ascii=False), encoding="utf-8"
        )

    # Merge per-dataset manifests so parallel runs never race on one file.
    combined = {}
    for name in ("ukdale", "whited"):
        p = RAW / f"manifest_{name}.json"
        if p.exists():
            data = json.loads(p.read_text(encoding="utf-8"))
            if name == "whited":
                data.pop("entries", None)  # keep the combined manifest small
            combined[name] = data
    manifest_path = RAW / "datasets_manifest.json"
    manifest_path.write_text(json.dumps(combined, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"manifest -> {manifest_path}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit("interrupted")
