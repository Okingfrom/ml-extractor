#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"
# Activate a virtualenv if exists in repo (common in cPanel setups)
if [ -d "$ROOT_DIR/.venv" ]; then
  source "$ROOT_DIR/.venv/bin/activate"
fi
# Install backend deps if needed
if [ -f "$ROOT_DIR/backend/requirements.txt" ]; then
  pip install --upgrade pip setuptools wheel
  pip install -r "$ROOT_DIR/backend/requirements.txt"
fi
# Serve the app on port 8000
exec uvicorn backend.main:app --host 0.0.0.0 --port 8000
