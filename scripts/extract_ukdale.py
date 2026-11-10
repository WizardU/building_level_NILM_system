"""Inspect and extract the UK-DALE HDF5 bundle (keeps only what we need)."""

from __future__ import annotations

import argparse
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--zip", type=Path, default=RAW / "ukdale.h5.zip")
    parser.add_argument("--out", type=Path, default=RAW / "ukdale.h5")
    parser.add_argument("--list", action="store_true", help="Only list archive contents")
    args = parser.parse_args()

    if not args.zip.exists():
        raise SystemExit(f"missing {args.zip}; run scripts/download_datasets.py --dataset ukdale")

    with zipfile.ZipFile(args.zip) as bundle:
        members = bundle.infolist()
        print(f"{args.zip.name}: {len(members)} members, {args.zip.stat().st_size/1024**3:.2f} GB")
        for member in members:
            print(f"  {member.file_size/1024**3:7.3f} GB  {member.filename}")
        if args.list:
            return

        target = next((m for m in members if m.filename.lower().endswith(".h5")), None)
        if target is None:
            raise SystemExit("no .h5 member found in archive")
        if args.out.exists() and args.out.stat().st_size == target.file_size:
            print(f"already extracted: {args.out}")
            return

        print(f"extracting {target.filename} -> {args.out} ...", flush=True)
        args.out.parent.mkdir(parents=True, exist_ok=True)
        with bundle.open(target) as source, args.out.open("wb") as sink:
            while True:
                chunk = source.read(8 * 1024 * 1024)
                if not chunk:
                    break
                sink.write(chunk)
        print(f"done: {args.out} ({args.out.stat().st_size/1024**3:.2f} GB)")


if __name__ == "__main__":
    main()
