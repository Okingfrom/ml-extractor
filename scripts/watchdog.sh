#!/usr/bin/env bash
# Simple watchdog: ensures the run_backend_and_proxy.sh runner is running
# and attempts to restart it if the proxy/health endpoint fails.

REPO_DIR="/home/lmo/repositories/ml-extractor"
RUNNER="$REPO_DIR/scripts/run_backend_and_proxy.sh"
LOG="/home/lmo/run_backend_and_proxy.log"

set -euo pipefail

echo "$(date -u +'%Y-%m-%dT%H:%M:%SZ') Watchdog: checking services" >> "$LOG"

# Start runner if missing
if ! pgrep -f run_backend_and_proxy.sh >/dev/null 2>&1; then
  echo "$(date -u +'%Y-%m-%dT%H:%M:%SZ') Watchdog: runner not running — starting" >> "$LOG"
  nohup bash "$RUNNER" >> "$LOG" 2>&1 &
  sleep 1
fi

# Quick health check against the local proxy which should forward /api to backend
if ! curl -sS --max-time 3 http://127.0.0.1:8000/api/health >/dev/null 2>&1; then
  echo "$(date -u +'%Y-%m-%dT%H:%M:%SZ') Watchdog: proxy health failed — restarting runner" >> "$LOG"
  pkill -f run_backend_and_proxy.sh || true
  nohup bash "$RUNNER" >> "$LOG" 2>&1 &
  sleep 1
else
  echo "$(date -u +'%Y-%m-%dT%H:%M:%SZ') Watchdog: proxy health OK" >> "$LOG"
fi

exit 0
#!/usr/bin/env bash
# Simple watchdog for ml-extractor backend + proxy
# - Checks backend port (127.0.0.1:8001) and proxy port (127.0.0.1:8000)
# - If either is not listening, runs scripts/run_backend_and_proxy.sh
# Usage:
#   chmod +x scripts/watchdog.sh
#   nohup bash scripts/watchdog.sh > ~/run_backend_watchdog.log 2>&1 &
# Crontab example (run at reboot):
#   @reboot /bin/bash /home/<user>/repositories/ml-extractor/scripts/watchdog.sh > /home/<user>/run_backend_watchdog.log 2>&1

set -euo pipefail

# Adjust these if your setup differs
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUN_SCRIPT="$REPO_DIR/scripts/run_backend_and_proxy.sh"
LOG_FILE="$HOME/run_backend_watchdog.log"
CHECK_INTERVAL=30
BACKEND_HOST=127.0.0.1
BACKEND_PORT=8001
PROXY_PORT=8000

timestamp() { date -u +"%Y-%m-%dT%H:%M:%SZ"; }
log() { echo "$(timestamp) [watchdog] $*" | tee -a "$LOG_FILE"; }

is_port_listening() {
  local host="$1" port="$2"
  # Prefer nc, then ss, then lsof/pgrep fallback
  if command -v nc >/dev/null 2>&1; then
    nc -z "$host" "$port" >/dev/null 2>&1
    return $?
  fi
  if command -v ss >/dev/null 2>&1; then
    ss -ltn | grep -q ":${port} \|:${port}$"
    return $?
  fi
  if command -v lsof >/dev/null 2>&1; then
    lsof -i TCP:"${port}" | grep -q LISTEN
    return $?
  fi
  # Last resort: check for common process names
  pgrep -f "uvicorn" >/dev/null 2>&1 && return 0
  pgrep -f "server_proxy_switch.py" >/dev/null 2>&1 && return 0
  return 1
}

ensure_run_script_exists() {
  if [ ! -x "$RUN_SCRIPT" ]; then
    if [ -f "$RUN_SCRIPT" ]; then
      log "Making run script executable: $RUN_SCRIPT"
      chmod +x "$RUN_SCRIPT" || true
    else
      log "ERROR: run script not found at $RUN_SCRIPT"
      exit 2
    fi
  fi
}

log "watchdog starting; repo=$REPO_DIR, run_script=$RUN_SCRIPT, log=$LOG_FILE"
ensure_run_script_exists

while true; do
  backend_ok=false
  proxy_ok=false

  if is_port_listening "$BACKEND_HOST" "$BACKEND_PORT"; then
    backend_ok=true
  fi
  if is_port_listening "$BACKEND_HOST" "$PROXY_PORT"; then
    proxy_ok=true
  fi

  if [ "$backend_ok" = false ] || [ "$proxy_ok" = false ]; then
    log "Detected service down (backend=$backend_ok proxy=$proxy_ok). Restarting via $RUN_SCRIPT"
    # Run the run script (non-blocking) and capture output to log
    nohup bash "$RUN_SCRIPT" >> "$LOG_FILE" 2>&1 &
    # give some time for services to come up
    sleep 5
  fi

  sleep "$CHECK_INTERVAL"
done
