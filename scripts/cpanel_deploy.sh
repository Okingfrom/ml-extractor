#!/bin/sh
set -e
# Usage: PASSENGER_VENV=/path/to/venv ./scripts/cpanel_deploy.sh

: "${PASSENGER_VENV:=}" 
REPO_DIR="/home/lmo/repositories/ml-extractor"

probe_common_venvs() {
  # common cPanel/passenger venv locations to try
  candidates="/home/lmo/virtualenv/repositories/ml-extractor/3.8 /opt/cpanel/ea-ruby24/root/usr/venv /usr/local/python3.8/venv /opt/python/3.8/venv"
  for p in $candidates; do
    if [ -x "$p/bin/pip" ]; then
      echo "$p"
      return 0
    fi
  done
  return 1
}

if [ -z "$PASSENGER_VENV" ]; then
  echo "[cpanel_deploy] PASSENGER_VENV not set, probing common locations..."
  found=$(probe_common_venvs || true)
  if [ -n "$found" ]; then
    PASSENGER_VENV="$found"
    echo "[cpanel_deploy] Found venv at: $PASSENGER_VENV"
  else
    PASSENGER_VENV="/home/lmo/virtualenv/repositories/ml-extractor/3.8"
    echo "[cpanel_deploy] No common venv found; defaulting to: $PASSENGER_VENV"
  fi
else
  echo "[cpanel_deploy] Using provided PASSENGER_VENV: $PASSENGER_VENV"
fi

if [ ! -x "$PASSENGER_VENV/bin/pip" ]; then
  echo "[cpanel_deploy] ERROR: pip not found in $PASSENGER_VENV/bin/pip" >&2
  exit 1
fi

mkdir -p "$REPO_DIR/uploads" "$REPO_DIR/backups" "$REPO_DIR/logs"

echo "[cpanel_deploy] Upgrading pip in target venv..."
"$PASSENGER_VENV/bin/pip" install --upgrade pip setuptools wheel || true

if [ "${SKIP_MAIN_REQUIREMENTS:-0}" = "1" ]; then
  echo "[cpanel_deploy] SKIP_MAIN_REQUIREMENTS=1 set; skipping install of main requirements.txt"
else
  echo "[cpanel_deploy] Installing repository requirements..."
  "$PASSENGER_VENV/bin/pip" install -r "$REPO_DIR/requirements.txt" || echo "[cpanel_deploy] Main requirements install failed"
fi

echo "[cpanel_deploy] Installing backend requirements..."
"$PASSENGER_VENV/bin/pip" install -r "$REPO_DIR/extractorml/backend/requirements.txt" || echo "[cpanel_deploy] Backend requirements install failed"

echo "[cpanel_deploy] Done"
