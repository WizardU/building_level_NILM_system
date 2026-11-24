# Live demo runbook — NILM midterm

> Target: 8–10 minutes, follows the 11/30 report and the 12/07 oral.
> Fallback: the same scenes are captured in `report_build/shots/` and the 11.25 deck.

## 0. Before the demo (one terminal each)

```powershell
# Backend
cd NILM\backend
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000

# Web
cd NILM\web
$env:TEMP="$PWD\..\report_build\tmp"; $env:TMP=$env:TEMP
npm run dev -- --host 127.0.0.1 --port 3000

# Mobile H5 (if needed)
cd NILM\mobile
npm run dev:h5
```

Check:

```powershell
curl.exe http://127.0.0.1:8000/readyz
# expect backend=onnx, models_ready=true, model_version=<hash>
```

Open `http://127.0.0.1:3000/`, log in as `admin / admin123`.

## 1. Dashboard — one meter, five appliances (2 min)

1. Building: **Building A · UK-DALE House 1**; Meter: **UK-DALE House 1 · Mains**.
2. Point at the KPI row: **State F1 76.2%, Event F1 79.7%, MAE 10.4 W** (test-set averages).
3. Click **Refresh**. The 599-point disaggregation stream and the 5 appliance cards update.
4. Say: "The navy line is the one measured meter; the coloured lines are the model's estimates. The next slide shows where they fail."

## 2. Replay — live data, not a static screenshot (2 min)

In a third terminal:

```powershell
cd NILM
python -m adapters.replay.cli --speed 80 --batch 5
```

- The dashboard's latest timestamp advances; the fridge card toggles ON/OFF.
- Point out that the same API feeds Web and mobile; no mock path.

If replay is not available, use the preloaded 14,400 samples and say "this is replay data, not a live meter".

## 3. Evaluation — the honest numbers (1 min)

Open **Evaluation**:

- Event F1 / State F1 bars for baseline / dilated / attention.
- Say: "Attention wins MAE and Event F1 on average; baseline still wins State F1; microwave is the weak class."
- Open **Analytics** → bill, unmetered energy, alert log.

## 4. Mobile H5 — same API (1 min)

Open the mobile H5 URL (default `http://127.0.0.1:3100`):

- Analytics: cost, energy breakdown, alert log.
- Show English-only UI.
- Say: "Same backend, same data; H5 today, WeChat/App next."

## 5. Alerts / ON-OFF (1 min)

- Raise the replay speed or use a high-power window; the alert log shows a threshold alert.
- Resolve it from the Web alert panel (if the UI is available).
- Say: "Alerts are deduplicated by the cooldown; resolve writes back to the DB."

## 6. Close (30 s)

"One meter, five appliances, real data, honest errors. The system works; the model claim is not universal yet. Next: focal/oversampling for microwave, cross-dataset, tests/CI."

## Fallbacks

| Failure | Fallback |
|---|---|
| Backend not ready | Play the 11.25 deck's Web screenshot; explain `/readyz` output |
| Web dev server fails | Use `report_build/shots/web_dashboard_tall.png` and `web_evaluation.png` |
| Mobile H5 fails | Use `report_build/shots/mobile_analytics.png` |
| Replay fails | Show the preloaded DB window; do not claim live data |
| Projector too small | Zoom the browser to 125%; keep the KPI row visible |

## Do not say

- "The model beats baseline everywhere." It does not (State F1 and cross-house Event F1).
- "WHITED is 44.1% accurate in general." It is a strict 20-device holdout with 18/40 classes evaluable.
- "Redis / Modbus / PostgreSQL are running." They are not.
