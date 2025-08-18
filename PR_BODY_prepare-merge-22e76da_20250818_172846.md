Title: Restore `app_improved.py` from commit 22e76da — prepare for merge into main

Summary
-------
This branch contains the restored `app_improved.py` (from commit `22e76da`) with a minimal, safe change: developer bypass flags have been disabled to make the app suitable for review and potential merge.

What changed
------------
- Restored `app_improved.py` (from commit `22e76da`) preserved in `backups/` and committed to this branch.
- Disabled developer bypass flags:
  - `DEVELOPER_MODE = False`
  - `DISABLE_AUTH = False`

Why
---
The restored file represents the UI the project previously used. Before merging into `main` we should verify it does not expose developer shortcuts and that authentication behaves correctly in staging.

Recommended QA steps
--------------------
1. Create and activate a python venv (use a machine with compatible CPU or a container):

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt || true
```

2. Start the restored app on a non-production port for inspection (we used port 5001 locally):

```bash
. venv_improved/bin/activate
FLASK_APP=app_improved.py FLASK_ENV=development flask run --host=127.0.0.1 --port=5001
```

3. Verify the following pages and behavior:
   - Index and upload flow: `/` — confirm UI layout and file upload works with sample files in `samples/`.
   - Auth: `/login` and `/logout` — ensure login flow works or that the app falls back gracefully.
   - Dev routes: `/dev-login` and `/switch-user/*` should not be available in production (they remain in code but are disabled by default flags).
   - Debug routes: `/debug-session`, `/test-auth` — inspect session handling and cookie behavior.

4. Manual Excel smoke test: upload `samples/sample_input.xlsx` and export to `samples/sample_output.xlsx`. Open result and validate columns match mapping in `config/mapping.yaml`.

5. Confirm no accidental changes to `main` or running backend on port 5000.

Edge cases and notes
--------------------
- The user's machine previously produced "Illegal instruction" errors for NumPy/Pandas on older CPUs. If tests import numpy/pandas and crash, run QA on a different machine or in a container with compatible wheels.
- If you want to remove dev routes entirely before merging, I can prepare a follow-up commit that deletes them (safer for production).

Merge checklist (minimal)
------------------------
- [ ] PR reviewed and approved by project owner.
- [ ] Basic QA steps completed (upload/download, auth checks).
- [ ] Optional: Remove dev-only routes or guard them behind a stricter feature flag.
- [ ] Tag created for the restore commit (already created: `vrestore-22e76da-20250818_172549`).

Notes for the maintainer
------------------------
- I created backups under `backups/app_improved_restored_22e76da_20250818_172549.py` and pushed a preserve branch for safety.
- If you'd like, I can also open a PR body on GitHub for you, but I don't have your GitHub token; instead you can copy this file into the PR description when creating the PR from the branch `prepare-merge-22e76da_20250818_172846`.

Prepared-by: local maintainer script
