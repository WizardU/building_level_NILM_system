"""Capture authenticated screenshots of the running Web and mobile H5 apps."""

from __future__ import annotations

import base64
import json
import time
import urllib.request
from pathlib import Path

import websocket

CDP = "http://127.0.0.1:9222"
OUT = Path(__file__).resolve().parent / "shots"
OUT.mkdir(parents=True, exist_ok=True)


def api_token() -> str:
    request = urllib.request.Request(
        "http://127.0.0.1:8000/api/v1/auth/login",
        data=json.dumps({"username": "admin", "password": "admin123"}).encode(),
        headers={"Content-Type": "application/json"},
    )
    return json.loads(urllib.request.urlopen(request, timeout=30).read())["data"]["access_token"]


def page_target() -> str:
    targets = json.loads(urllib.request.urlopen(CDP + "/json/list", timeout=10).read())
    for target in targets:
        if target.get("type") == "page":
            return target["webSocketDebuggerUrl"]
    raise RuntimeError("no page target")


class Session:
    def __init__(self) -> None:
        self.ws = websocket.create_connection(page_target(), timeout=60, suppress_origin=True)
        self.next_id = 0

    def send(self, method: str, params: dict | None = None) -> dict:
        self.next_id += 1
        self.ws.send(json.dumps({"id": self.next_id, "method": method, "params": params or {}}))
        while True:
            message = json.loads(self.ws.recv())
            if message.get("id") == self.next_id:
                if "error" in message:
                    raise RuntimeError(f"{method}: {message['error']}")
                return message.get("result", {})

    def eval(self, expression: str) -> None:
        self.send("Runtime.evaluate", {"expression": expression, "awaitPromise": True})

    def viewport(self, width: int, height: int, mobile: bool = False) -> None:
        self.send(
            "Emulation.setDeviceMetricsOverride",
            {
                "width": width,
                "height": height,
                "deviceScaleFactor": 1 if not mobile else 2,
                "mobile": mobile,
            },
        )

    def goto(self, url: str) -> None:
        self.send("Page.navigate", {"url": url})

    def shot(self, name: str) -> Path:
        time.sleep(1)
        data = self.send("Page.captureScreenshot", {"format": "png", "captureBeyondViewport": False})
        path = OUT / name
        path.write_bytes(base64.b64decode(data["data"]))
        print(f"saved {path} ({path.stat().st_size // 1024} KB)")
        return path


def main() -> None:
    token = api_token()
    session = Session()
    session.send("Page.enable")
    session.send("Runtime.enable")

    session.viewport(1600, 900, mobile=False)
    session.goto("http://localhost:3000/login")
    time.sleep(3)
    session.eval(
        "localStorage.setItem('access_token', %s);"
        "localStorage.setItem('refresh_token', %s);"
        "localStorage.setItem('lang', 'en');"
        "localStorage.setItem('building_id', '1');"
        "localStorage.setItem('meter_id', '101');"
        % (json.dumps(token), json.dumps(token))
    )

    for name, path, wait in [
        ("web_dashboard.png", "/", 14),
        ("web_evaluation.png", "/evaluation", 8),
        ("web_analytics.png", "/analytics", 8),
    ]:
        session.goto("http://localhost:3000" + path)
        time.sleep(wait)
        session.shot(name)

    # Mobile H5 (uni-app hash router)
    session.viewport(390, 844, mobile=True)
    session.goto("http://127.0.0.1:3100/")
    time.sleep(3)
    session.eval(
        "localStorage.setItem('access_token', %s);"
        "localStorage.setItem('building_id', '1');"
        "localStorage.setItem('meter_id', '101');" % json.dumps(token)
    )
    for name, path, wait in [
        ("mobile_home.png", "#/pages/home/home", 12),
        ("mobile_analytics.png", "#/pages/analytics/analytics", 8),
    ]:
        session.goto("http://127.0.0.1:3100/" + path)
        time.sleep(wait)
        session.shot(name)

    session.ws.close()


if __name__ == "__main__":
    main()
