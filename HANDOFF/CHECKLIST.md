# Handoff checklist

## Before commit / push

- [ ] Working tree contains no `data/`, `.pt`, `.onnx`, `.joblib`, `.venv`, `node_modules`, `nilm.db`.
- [ ] No secrets, tokens, WEMUST files, or private screenshots.
- [ ] `python -m py_compile` passes for changed Python files.
- [ ] Backend starts; `/readyz` says `backend=onnx` (or explicitly `heuristic` if models absent).
- [ ] `scripts/smoke_api.py` passes 21/21.
- [ ] Mobile H5 builds/loads; four tabs visible; English-only.
- [ ] `openapi/NILM.json` is regenerated if routes changed.
- [ ] `HANDOFF/ENGINEERING_MOBILE.md` matches actual code (no Redis/Postgres claim).
- [ ] `HANDOFF/ALGORITHM_PROVISIONAL.md` clearly labels provisional work and Yang's ownership.

## Branch / tag

- [ ] Branch: `handoff/ysb-engineering-midterm`
- [ ] Commit message: `feat(ysb): backend API + Uni-app H5 handoff and evidence`
- [ ] Tag: `handoff-ysb-2026-11-25`
- [ ] Push to personal origin (and course repo if access exists).
- [ ] Record the short hash in `HANDOFF/EVIDENCE.md` / report.

## Report fields

- [ ] Replace `[TBD: YSB backend & mobile commits]` with branch/tag/hash.
- [ ] Correct "Redis/PostgreSQL" if not implemented.
- [ ] Correct "18.64 ms" if the new measurement differs.
- [ ] Mark native builds and Modbus/MQTT as deferred (W7), not completed.

## Handoff to Yang

- [ ] Yang has read `ALGORITHM_PROVISIONAL.md`.
- [ ] Yang has the local `data/processed` or will replace it with M1's official data.
- [ ] Yang has reviewed the 8-epoch MSE vs report's 3-epoch numbers.
- [ ] Yang accepts or rejects the provisional `ml/` results in writing (commit message/issue).
- [ ] YSB stops changing `ml/` after the handoff tag.

## Handoff to Jin

- [ ] Jin confirms M1 official preprocessing output location.
- [ ] Jin confirms whether local `data/processed` differs.
- [ ] Jin owns `web/` and M1; YSB does not claim them.
