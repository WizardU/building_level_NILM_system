# Course repo integration

## Current reality

- This workspace's `origin` is **personal**: `https://github.com/WizardU/building_level_NILM_system.git`
- The progress report names the course repo: **`MUST-BIT-BEIE-FYP-2026/fyp-2026-042`**
- That course repo is **not configured** as a remote here, and its history is not the same as this repo's
  short history (`ce8c55c` is the local base). Do not pretend the hashes are interchangeable.

## Option A — you have access to the course repo (preferred)

```powershell
cd NILM
git remote add course https://github.com/MUST-BIT-BEIE-FYP-2026/fyp-2026-042.git
git fetch course
git checkout -b handoff/usp-engineering-midterm course/main
```

Copy only USP-owned paths from this workspace into the course branch:

```text
backend/
mobile/
openapi/
scripts/smoke_api.py
scripts/demo_web.*
scripts/demo_mobile.*
HANDOFF/
```

Then:

```powershell
git add backend mobile openapi scripts HANDOFF
git commit -m "feat(usp): backend API + Uni-app H5 handoff and evidence"
git tag handoff-usp-2026-11-25
git push -u course handoff/usp-engineering-midterm
```

If your identity is not configured:

```powershell
git config user.name "U SENGPAN"
git config user.email "<your GitHub email>"
```

## Option B — no course access yet

1. Push the handoff branch to the personal remote (below).
2. Send the course-repo owner:
   - branch name + tag;
   - `HANDOFF/ENGINEERING_MOBILE.md`;
   - `HANDOFF/EVIDENCE.md`;
   - a ZIP of `backend/`, `mobile/`, `openapi/`, `scripts/smoke_api.py`, `HANDOFF/`.
3. After they create the course branch, replace `[TBD: USP backend & mobile commits]` in the report
   with the course commit hash.

## Option C — patch/bundle

Because the histories differ, a `git format-patch` of this branch only contains the handoff docs,
not the full backend/mobile tree. Prefer a ZIP/tree copy. If a bundle is required:

```powershell
git bundle create ..\NILM_USP_ENGINEERING_2026-11-25.bundle handoff/usp-engineering-midterm
```

The course repo can `git fetch <bundle> handoff/usp-engineering-midterm:handoff/usp-engineering-midterm`
only if it accepts an unrelated history; otherwise copy the tree.

## Personal remote push (this workspace)

```powershell
git push -u origin handoff/usp-engineering-midterm
git push origin handoff-usp-2026-11-25
```

If authentication fails, keep the local branch; do not rewrite `origin`.

## Report line to replace

`[TBD: USP backend & mobile commits]` →

> U SENGPAN — midterm M2 ML training/ONNX/eval + M3 backend + M5 mobile H5:
> `handoff/usp-engineering-midterm`, tag `handoff-usp-2026-11-25`, commit `<hash>` (course repo).
> 10 ONNX models, 8-epoch tables, WHITED RF 44.1%, 21/21 API checks, OpenAPI 38 paths.

Also update the M2 owner row: midterm M2 = U SENGPAN; W5+ improvements = Yang Yifei.
