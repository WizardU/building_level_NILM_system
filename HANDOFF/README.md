# YSB engineering / mobile handoff

**Owner:** U SENGPAN (student ID 1230001605)  
**Scope:** M3 backend/API + M5 Uni-app mobile H5 (primary: mobile; shared: backend)  
**Date:** 2026-11-25  
**Branch:** `handoff/ysb-engineering-midterm`  
**Tag:** `handoff-ysb-2026-11-25`

> The algorithm work in `ml/` is **provisional local scaffolding**, not YSB's final contribution.
> Official ownership follows the progress report: M1 preprocessing = Jin Xinyi, M2 model/eval = Yang Yifei.
> Read [ALGORITHM_PROVISIONAL.md](ALGORITHM_PROVISIONAL.md) before using any `ml/` artifact in the final report.

## What is in this folder

| File | Purpose |
|---|---|
| [ENGINEERING_MOBILE.md](ENGINEERING_MOBILE.md) | YSB's actual backend/mobile delivery, run commands, evidence, gaps |
| [ALGORITHM_PROVISIONAL.md](ALGORITHM_PROVISIONAL.md) | Temporary algorithm work to hand to Yang Yifei; data gaps and caveats |
| [EVIDENCE.md](EVIDENCE.md) | 21 API checks, screenshots, commits/tags, reproducibility commands |
| [REPO_MAP.md](REPO_MAP.md) | Which directory belongs to which owner and what is production/provisional |
| [COURSE_REPO_INTEGRATION.md](COURSE_REPO_INTEGRATION.md) | How to port this branch into the course GitHub repo |
| [CHECKLIST.md](CHECKLIST.md) | Pre-push / pre-merge / handoff checklist |

## Ownership matrix (from the progress report)

| Member | Report role | Owns in this repo | Not owned here |
|---|---|---|---|
| Jin Xinyi | Data Pipeline & Web Frontend Lead | `ml/preprocess/` (official M1), `web/` (M4), Docker/Nginx | M2 model/eval, M3/M5 |
| Yang Yifei | AI & Algorithm Modeling Lead | `ml/models/`, `ml/train/`, `ml/eval/`, ONNX training | M1, M3/M4/M5 |
| U SENGPAN | Backend API & Mobile App Lead | `backend/`, `mobile/`, `openapi/`, `scripts/smoke_api.py` | M1/M2, M4 Web |

## The one-paragraph handoff

YSB delivered the FastAPI backend + Uni-app H5 mobile client and the contract evidence (21 API checks, screenshots, run scripts). The local `ml/` training/eval stack was built only because the official M1 preprocessed data was not available in this workspace; it is frozen as a provisional evidence branch for Yang Yifei to review, reproduce, or replace. Do not merge `ml/` provisional results into the final report without Yang's sign-off. The course repo needs the same branch under `handoff/ysb-engineering-midterm`, then the report's `[TBD: YSB commits]` entries can be replaced by the branch/tag hashes.

## Quick start for a reviewer

```powershell
cd NILM\backend
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000

# another terminal
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
