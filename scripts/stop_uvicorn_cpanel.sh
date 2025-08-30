#!/usr/bin/env bash
PID_DIR="../run"
if [ -f "$PID_DIR/uvicorn.pid" ]; then
  PID=$(cat "$PID_DIR/uvicorn.pid")
  if kill -0 "$PID" 2>/dev/null; then
    kill "$PID" && echo "Stopped uvicorn pid $PID" || echo "Failed to kill $PID"
  else
    echo "No process with pid $PID. Removing stale pid file."
  fi
  rm -f "$PID_DIR/uvicorn.pid"
else
  echo "No uvicorn.pid found. Is uvicorn running?"
fi
