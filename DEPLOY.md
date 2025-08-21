# Deploy Helper

A small helper script to deploy the project to a server via SSH/cPanel terminal.

## Files Added

- scripts/deploy_to_server.sh — minimal deploy script (clone/pull, venv, pip, gunicorn)
- .env.template — example environment variables file

## Usage

1. Copy `.env.template` to `.env` and fill secrets.
2. On the server, run: ./scripts/deploy_to_server.sh /path/to/deploy main

Notes:
- The script uses gunicorn to start `app_improved:app` on 127.0.0.1:8000. If your host uses Passenger or a different process manager, adapt accordingly.
- The script will create a `.venv` in the deploy directory and install `requirements.txt`.
- If your hosting provider doesn't support building compiled wheels for numpy/pandas, consider using the Flask fallback (`app_flask.py`) or using a container.
