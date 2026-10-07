"""Push replay samples into backend measurements API."""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from adapters.replay.source import ReplaySource


def main() -> None:
    p = argparse.ArgumentParser(description="UK-DALE/synthetic meter replay")
    p.add_argument("--api", default="http://127.0.0.1:8000/api/v1")
    p.add_argument("--meter-id", type=int, default=101)
    p.add_argument("--speed", type=float, default=10.0, help="samples per second")
    p.add_argument("--username", default="admin")
    p.add_argument("--password", default="admin123")
    p.add_argument(
        "--npz",
        type=Path,
        default=ROOT / "data" / "processed" / "replay" / "synth_house1_day1.npz",
    )
    p.add_argument("--batch", type=int, default=5)
    args = p.parse_args()

    if not args.npz.exists():
        raise SystemExit(
            f"Missing {args.npz}. Run: cd ml && python -m preprocess.generate_synthetic"
        )

    src = ReplaySource(args.npz, loop=True)
    with httpx.Client(timeout=30) as client:
        r = client.post(
            f"{args.api}/auth/login",
            json={"username": args.username, "password": args.password},
        )
        r.raise_for_status()
        token = r.json()["data"]["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print(f"Replaying {args.npz} → meter {args.meter_id} @ {args.speed} Hz")
        buf = []
        while True:
            sample = src.read()
            if sample is None:
                break
            buf.append(sample.to_api())
            if len(buf) >= args.batch:
                resp = client.post(
                    f"{args.api}/measurements/upload",
                    headers=headers,
                    json={"meter_id": args.meter_id, "samples": buf},
                )
                resp.raise_for_status()
                buf.clear()
                time.sleep(args.batch / args.speed)


if __name__ == "__main__":
    main()
