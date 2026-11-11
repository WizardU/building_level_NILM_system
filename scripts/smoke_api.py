"""End-to-end API smoke test against a running backend.

Usage: python scripts/smoke_api.py [--base http://127.0.0.1:8000]
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone


def call(base: str, path: str, method: str = "GET", body=None, token: str | None = None):
    url = base + path
    data = json.dumps(body).encode("utf-8") if body is not None else None
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(request, timeout=60) as response:
        payload = json.loads(response.read().decode("utf-8"))
    if isinstance(payload, dict) and "data" in payload:
        return payload["data"]
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", default="http://127.0.0.1:8000")
    args = parser.parse_args()
    api = args.base.rstrip("/") + "/api/v1"
    failures: list[str] = []

    def check(name: str, condition: bool, detail: str = "") -> None:
        print(f"{'PASS' if condition else 'FAIL'}  {name}  {detail}")
        if not condition:
            failures.append(name)

    ready = call(args.base.rstrip("/"), "/readyz")
    check("readyz", ready.get("status") in ("ok", "degraded"), json.dumps(ready.get("inference", {}), ensure_ascii=False))
    check("onnx backend", ready.get("inference", {}).get("backend") == "onnx", ready.get("inference", {}).get("backend", ""))

    login = call(api, "/auth/login", "POST", {"username": "admin", "password": "admin123"})
    token = login["access_token"]
    check("login", bool(token))

    buildings = call(api, "/buildings", token=token)
    check("buildings", buildings.get("total", 0) >= 1, str([b["name"] for b in buildings.get("items", [])]))

    meters = call(api, "/meters", token=token)
    check("meters", meters.get("total", 0) >= 1, str([m["name"] for m in meters.get("items", [])]))
    meter_id = meters["items"][0]["id"]

    realtime = call(api, f"/measurements/realtime?meter_id={meter_id}", token=token)
    check("realtime", "timestamp" in realtime, f"{realtime.get('timestamp')} {realtime.get('total_power_kw')} kW")

    current = call(api, f"/meters/{meter_id}/current", token=token)
    check("meter current alias", "phase_a" in current)

    apps = call(api, f"/appliances?meter_id={meter_id}", token=token)
    first_app = apps["items"][0]
    usage = call(api, f"/appliances/{first_app['id']}/usage", token=token)
    check(
        "appliance usage",
        usage.get("available") is True,
        f"{first_app['type']} {usage.get('energy_kwh')} kWh",
    )

    now = datetime.now(timezone.utc).replace(second=0, microsecond=0)
    start = now - timedelta(hours=2)
    query = urllib.parse.urlencode(
        {
            "meter_id": meter_id,
            "start": start.isoformat().replace("+00:00", "Z"),
            "end": now.isoformat().replace("+00:00", "Z"),
        }
    )

    begun = time.time()
    result = call(api, f"/disaggregation/result?{query}", token=token)
    elapsed = time.time() - begun
    appliances = result.get("appliances", [])
    check("result backend", result.get("backend") == "onnx", result.get("backend", ""))
    check("result appliances", len(appliances) == 5, str([a["type"] for a in appliances]))
    check("result series", len(result.get("mains_series", [])) > 0, f"{len(result.get('mains_series', []))} points, {elapsed:.2f}s")
    check("timestamps Z", result.get("start", "").endswith("Z"), result.get("start", ""))

    task = call(api, "/disaggregation/run", "POST", {"meter_id": meter_id, "start": start.isoformat().replace("+00:00", "Z"), "end": now.isoformat().replace("+00:00", "Z")}, token=token)
    status = {}
    for _ in range(30):
        status = call(api, f"/disaggregation/status/{task['task_id']}", token=token)
        if status.get("status") in ("completed", "failed"):
            break
        time.sleep(1)
    check("async task", status.get("status") == "completed", status.get("status", ""))

    overview = call(api, f"/disaggregation/overview?meter_id={meter_id}", token=token)
    check("overview", overview.get("totalDevices") == 5, f"mains={overview.get('mainsPower')}W f1={overview.get('f1Score')} eventF1={overview.get('eventF1')} latency={overview.get('latency')}ms")

    energy = call(api, f"/analytics/energy?meter_id={meter_id}", token=token)
    check("energy", energy.get("totalKWh", 0) > 0, f"{energy.get('totalKWh')} kWh, {len(energy.get('breakdown', []))} rows")

    reports = call(api, "/analytics/reports", token=token)
    check("reports", len(reports.get("per_appliance", [])) == 10, f"{len(reports.get('per_appliance', []))} rows, samples={reports.get('samples')}")
    check("reports no fake speed", all(v <= 100 for s in reports.get("series", []) for v in s["value"]), str([s["value"] for s in reports.get("series", [])]))

    metrics = call(api, "/analytics/metrics", token=token)
    check("metrics", metrics.get("samples", 0) > 0, str(metrics.get("samples")))

    settings = call(api, "/analytics/settings", token=token)
    check("settings", settings.get("power_limit_w", 0) > 0, json.dumps(settings, ensure_ascii=False))

    whited = call(api, "/datasets/whited", token=token)
    check(
        "whited dataset",
        whited.get("available") is True,
        f"{whited.get('index', {}).get('classes')} classes",
    )

    alerts = call(api, f"/analytics/alerts?building_id=1", token=token)
    check("alerts", alerts.get("total", 0) >= 1, alerts["items"][0].get("title_en", "") if alerts.get("items") else "")

    print()
    if failures:
        print(f"{len(failures)} check(s) failed: {failures}")
        return 1
    print("all checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
