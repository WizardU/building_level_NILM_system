# NILM Mobile Client

Cross-platform client (H5 / WeChat mini-program / Android / iOS) for the
building-level NILM system, built with uni-app + Vue 3.

The UI is **English only** by design.

## Requirements

- Node.js **>= 22.12** (required by the pinned uni-app alpha packages)
- The FastAPI backend running at `http://127.0.0.1:8000`

A portable Node 22 lives in `../.tools/node-v22.14.0-win-x64` after the first
Web demo run, or download it from <https://nodejs.org/dist/v22.14.0/>.

## Configure the backend

Edit `src/utils/config.js`:

```js
// Local browser / emulator
export const API_BASE = 'http://127.0.0.1:8000/api/v1'

// Physical phone on the same Wi-Fi
// export const API_BASE = 'http://192.168.1.100:8000/api/v1'
```

The backend CORS list already allows `localhost:3100` and `127.0.0.1:3100`.

## Run

```powershell
# from the repository root
.\scripts\demo_mobile.ps1
```

Or manually, with Node 22 first on PATH:

```powershell
cd mobile
npm install
npm run dev:h5
```

Open <http://127.0.0.1:3100> and sign in with `admin` / `admin123`.

## Build

```powershell
npm run build:h5          # -> dist/build/h5
npm run dev:mp-weixin     # WeChat mini-program
npm run build:app         # App (needs HBuilderX for packaging)
```

Verified in this repo: `npm run build:h5` completes with uni-app 5.32.

## Screens

| Tab | Content |
|-----|---------|
| Monitor | Mains power, active devices, State F1 / Event F1, live curves, appliance list, manual refresh |
| Devices | Per-appliance power, energy, model F1 and ON threshold, All/Running/Idle filter |
| Analytics | Energy breakdown, unmetered energy, estimated cost, alert log with Resolve |
| Profile | Power alert threshold (persisted to the backend), About, Sign out |

## Notes

- The client uses the same REST API as the Web console; there is no mock layer.
- The replay adapter supplies live samples; the backend also preloads one day of
  real UK-DALE data on first start, so charts are populated immediately.
- Alert banners respect the threshold stored in `GET /analytics/settings`.
