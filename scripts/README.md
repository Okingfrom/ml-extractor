Uvicorn start/stop scripts for cPanel

Usage:
1. Edit `start_uvicorn_cpanel.sh` and set `VENV_PATH` to your cPanel app virtualenv activate script path.
2. Upload the repository to your cPanel app directory or copy the `scripts/` folder into your app root.
3. Make scripts executable:
   chmod +x scripts/start_uvicorn_cpanel.sh scripts/stop_uvicorn_cpanel.sh

Start:
   ./scripts/start_uvicorn_cpanel.sh
Stop:
   ./scripts/stop_uvicorn_cpanel.sh

Notes:
- The scripts use ../logs and ../run relative to the repository root for logs and pid files. Adjust paths if your layout differs.
- On cPanel, prefer using the Python App manager if available; these scripts are a fallback for persistent uvicorn on shared hosts.
