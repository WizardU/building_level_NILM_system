from __future__ import annotations

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from capture_ui import Session, api_token

token = api_token()
session = Session()
session.send("Page.enable")
session.send("Runtime.enable")
session.viewport(1600, 1100, mobile=False)
session.goto("http://localhost:3000/login")
time.sleep(3)
session.eval(
    "localStorage.setItem('access_token', %s);"
    "localStorage.setItem('refresh_token', %s);"
    "localStorage.setItem('lang', 'en');"
    "localStorage.setItem('building_id', '1');"
    "localStorage.setItem('meter_id', '101');" % (f'"{token}"', f'"{token}"')
)
session.goto("http://localhost:3000/")
time.sleep(14)
session.shot("web_dashboard_tall.png")
session.ws.close()
