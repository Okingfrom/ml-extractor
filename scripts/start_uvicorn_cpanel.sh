#!/usr/bin/env bash
# Start script for running uvicorn on cPanel/shared hosting
# - Uses a virtualenv path if provided
# - Starts uvicorn via setsid + nohup and writes PID to run/uvicorn.pid

# Configuration (edit these variables for your server)
VENV_PATH="/home/your-user/virtualenv/repositories/ml-extractor/3.8/bin/activate"
APP_MODULE="backend.main:app"
HOST="127.0.0.1"
PORT="8000"
LOG_DIR="../logs"
PID_DIR="../run"
UVICORN_CMD="python -m uvicorn $APP_MODULE --host $HOST --port $PORT --log-level info"

mkdir -p "$LOG_DIR" "$PID_DIR"

# Activate venv if present
if [ -f "$VENV_PATH" ]; then
  # shellcheck disable=SC1090
  source "$VENV_PATH"
fi

# Prevent duplicate runs
if [ -f "$PID_DIR/uvicorn.pid" ]; then
  if kill -0 "$(cat $PID_DIR/uvicorn.pid)" 2>/dev/null; then
    echo "Uvicorn appears to be running (pid $(cat $PID_DIR/uvicorn.pid)). Exiting." >&2
    exit 0
  else
    echo "Stale PID file found. Removing." >&2
    rm -f "$PID_DIR/uvicorn.pid"
  fi
fi

# Start the server detached
cd "$(dirname "$0")/.." || exit 1
setsid bash -c "nohup $UVICORN_CMD > \"$LOG_DIR/uvicorn.out\" 2>&1 < /dev/null & echo \$! > \"$PID_DIR/uvicorn.pid\"" || {
  echo "Failed to start uvicorn" >&2
  exit 2
}

sleep 1
echo "Started uvicorn; pid=$(cat $PID_DIR/uvicorn.pid)"
