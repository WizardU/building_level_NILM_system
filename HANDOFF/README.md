# USP midterm delivery & handoff

**Owner:** U SENGPAN (student ID 1230001605)  
**Midterm scope:** **M2 ML training/ONNX/evaluation (existing report work) + M3 backend/API + M5 Uni-app mobile H5**  
**Future M2 improvements:** Yang Yifei (W5+; see the report's W5/W6 plan)  
**Date:** 2026-11-25  
**Branch:** `handoff/usp-engineering-midterm`  
**Tag:** `handoff-usp-2026-11-25`

> Important correction: the midterm ML training/ONNX/WHITED baseline in the progress report is **USP's work**.
> The later improvements (dilated/Huber/3-seed/cross-house/REDD/PLAID/WHITED CNN) are handed to Yang.
> M1 official preprocessing remains Jin Xinyi's; USP's `data/processed` is a local fallback, not the official M1 output.

## What is in this folder

| File | Purpose |
|---|---|
| [ENGINEERING_MOBILE.md](ENGINEERING_MOBILE.md) | USP's backend/mobile delivery, run commands, evidence, gaps |
| [ALGORITHM_PROVISIONAL.md](ALGORITHM_PROVISIONAL.md) | Midterm ML work (USP) + future improvement handoff (Yang) + data caveats |
| [EVIDENCE.md](EVIDENCE.md) | 21 API checks, screenshots, commits/tags, reproducibility commands |
| [REPO_MAP.md](REPO_MAP.md) | Directory ownership and production/provisional boundary |
| [REPORT_CORRECTION.md](REPORT_CORRECTION.md) | Exact contribution-table changes needed in the progress report |
| [COURSE_REPO_INTEGRATION.md](COURSE_REPO_INTEGRATION.md) | How to port this branch into the course GitHub repo |
| [CHECKLIST.md](CHECKLIST.md) | Pre-push / pre-merge / handoff checklist |

## Ownership matrix (corrected)

| Member | Report role | Owns in this repo | Not owned here |
|---|---|---|---|
| Jin Xinyi | Data Pipeline & Web Frontend Lead | official M1 preprocessing, `web/` (M4), Docker/Nginx | M2 training, M3/M5 |
| **U SENGPAN** | Backend & Mobile Lead + **midterm M2 training** | `backend/`, `mobile/`, `openapi/`, `scripts/smoke_api.py`; `ml/models/`, `ml/train/`, `ml/eval/` midterm training; midterm ONNX/WHITED RF | official M1 data; future M2 improvements |
| Yang Yifei | AI & Algorithm Modeling Lead (W5+) | future M2 improvements: dilated/Huber, 3-seed, cross-house, REDD/PLAID, WHITED CNN | midterm M2 training; M1/M3/M4/M5 |

## The one-paragraph handoff

USP delivered the midterm M2 training/ONNX/evaluation work plus the FastAPI backend and Uni-app H5 client. The local `ml/preprocess`/`data/processed` stack was built because the official M1 preprocessed data was not available in this workspace; it must not be presented as M1's deliverable. The **midterm** 8-epoch/10-ONNX/WHITED-RF results belong to USP; the **future** M2 improvements are Yang's W5+ scope. The report's 3-epoch text is stale and must be replaced using `REPORT_CORRECTION.md`. The course repo needs the same branch under `handoff/usp-engineering-midterm`.

## Quick start

```powershell
cd NILM\backend
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000

cd NILM
.\ml\.venv\Scripts\python.exe scripts\smoke_api.py
# expected: all checks passed (21)
```

Mobile H5:

```powershell
cd NILM\mobile
npm run dev:h5
```

See [ENGINEERING_MOBILE.md](ENGINEERING_MOBILE.md) for the full sequence.
