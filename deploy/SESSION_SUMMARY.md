Session summary — ML Extractor (short-lived memory)

Purpose
- Keep a concise, persistent record of what we did during this session so you (or other contributors) can pick up work without reading the entire chat history.

Status (as of 2025-08-30)
- Backend: Daphne running at 127.0.0.1:8000 using venv: /home/lmo/virtualenv/repositories/ml-extractor/3.8
  - Command used to start:
    nohup /home/lmo/virtualenv/repositories/ml-extractor/3.8/bin/daphne -b 127.0.0.1 -p 8000 simple_backend:app > /home/lmo/daphne.log 2>&1 &
  - Verified endpoints: GET /openapi.json (200), /docs (200)
- Frontend: build artifacts should be deployed to /home/lmo/public_html/extractorml.uy/ (index.html at root)
  - Build locally (or on server) from `frontend/`: `npm ci && npm run build`
  - Deploy: `rsync -avz frontend/build/ your@server:/home/lmo/public_html/extractorml.uy/`
- Logs: repo `logs/` contains `debug.log` (rotating) and `app.log` (INFO). Daphne stdout -> /home/lmo/daphne.log
- Repo changes made in this session (high level):
  - Added frontend deploy docs and script (deploy/frontend.*, scripts/deploy_frontend.sh)
  - Hardened logging: `backend/core/logging_config.py` now creates rotating `logs/debug.log` and `logs/app.log`
  - `simple_backend.py` now reuses centralized logging setup
  - Added `scripts/deploy_frontend.sh` and `deploy/frontend.htaccess`
  - Added session summary (this file)

Quick copy/paste commands (run on server)
- Pull latest code:
  cd /home/lmo/repositories/ml-extractor
  git pull origin main

- Start/stop Daphne (venv binary):
  pkill -f '/home/lmo/virtualenv/repositories/ml-extractor/3.8/bin/daphne' || true
  nohup /home/lmo/virtualenv/repositories/ml-extractor/3.8/bin/daphne -b 127.0.0.1 -p 8000 simple_backend:app > /home/lmo/daphne.log 2>&1 &

- Check logs & health:
  tail -n 200 /home/lmo/daphne.log
  tail -n 200 /home/lmo/repositories/ml-extractor/logs/debug.log
  tail -n 200 /home/lmo/repositories/ml-extractor/logs/app.log
  curl -I http://127.0.0.1:8000/openapi.json

- Deploy frontend using included script (edit top variables first):
  bash scripts/deploy_frontend.sh

Next recommended steps (pick one or more)
- Install a systemd unit for Daphne and use the provided CLI wrapper (`ml-extractor`) to manage it (I can add files under `deploy/` for quick install).
- Install logrotate for repo logs (`/etc/logrotate.d/ml-extractor`) — I can create the snippet.
- Optionally create a .deb package for easy install/uninstall.

Where to look in the repo
- Backend entrypoints: `backend/main.py`, `simple_backend.py`
- Logging: `backend/core/logging_config.py`
- Deploy helper scripts and docs: `deploy/` and `scripts/`

How this file should be used
- Treat this as the short-term session memory. Update it with a new section when you make deploy or critical config changes. It's intentionally small so it stays readable.

If you'd like, I can also:
- Add a one-line CLI program (`/usr/local/bin/ml-extractor`) and a `deploy/systemd` folder with unit + logrotate files to copy to `/etc` and `/usr/local/bin` respectively.
- Convert this summary into an issue or checklist in the repo's issue tracker (if you use GitHub and want a persistent task card).

End of session summary.
