#!/usr/bin/env bash
# Run backend (daphne) on BACKEND_PORT and start the aiohttp proxy on PROXY_PORT
# Usage: ./scripts/run_backend_and_proxy.sh 8001 8000

set -euo pipefail

REPO_DIR="/home/lmo/repositories/ml-extractor"
VENV_PY="/home/lmo/virtualenv/repositories/ml-extractor/3.8/bin/python"
VENV_DAPHNE="/home/lmo/virtualenv/repositories/ml-extractor/3.8/bin/daphne"

BACKEND_PORT=${1:-8001}
PROXY_PORT=${2:-8000}

echo "Stopping existing daphne and server_proxy processes (if any)"
pkill -f daphne || true
pkill -f server_proxy || true
sleep 1

# Ensure log file exists and is writable so nohup output is visible
LOG_FILE="${REPO_DIR}/run_backend_and_proxy.log"
mkdir -p "$(dirname "${LOG_FILE}")"
touch "${LOG_FILE}" || true
echo "=== $(date -u +'%Y-%m-%dT%H:%M:%SZ') Starting run_backend_and_proxy.sh ===" >> "${LOG_FILE}"

# Sanity checks for required binaries
echo "Checking expected executables:" >> "${LOG_FILE}"
if [ ! -x "${VENV_PY}" ]; then
	echo "ERROR: Python binary not found or not executable at ${VENV_PY}" | tee -a "${LOG_FILE}"
	echo "Check your virtualenv path or adjust VENV_PY in this script." | tee -a "${LOG_FILE}"
	exit 1
fi
if [ ! -x "${VENV_DAPHNE}" ]; then
	echo "WARN: Daphne executable not found at ${VENV_DAPHNE}, will try 'python -m daphne' fallback" | tee -a "${LOG_FILE}"
fi

# Derive site-packages from the selected python so we can set PYTHONPATH for the proxy
SITE_PACKAGES=$(${VENV_PY} -c "import site, sys; print('\n'.join(site.getsitepackages()))" 2>/dev/null || true)
if [ -n "${SITE_PACKAGES}" ]; then
	# Use the first discovered site-packages path
	FIRST_SITE=$(echo "${SITE_PACKAGES}" | head -n1)
	export PYTHONPATH="${FIRST_SITE}:${PYTHONPATH:-}"
	echo "Using PYTHONPATH=${FIRST_SITE}" | tee -a "${LOG_FILE}"
else
	echo "Could not detect venv site-packages; proxy may fail to import installed packages" | tee -a "${LOG_FILE}"
fi

echo "Starting backend on 127.0.0.1:${BACKEND_PORT} (using python -m uvicorn)"
# Use uvicorn (module) to run the FastAPI app via the selected python interpreter.
nohup "${VENV_PY}" -m uvicorn simple_backend:app --host 127.0.0.1 --port "${BACKEND_PORT}" --log-level info >> "${REPO_DIR}/server.log" 2>&1 &
echo "Backend started (logs: ${REPO_DIR}/server.log)" | tee -a "${LOG_FILE}"

echo "Starting proxy to forward /api -> 127.0.0.1:${BACKEND_PORT} on 127.0.0.1:${PROXY_PORT}"
nohup "${VENV_PY}" "${REPO_DIR}/scripts/server_proxy_switch.py" --backend-port "${BACKEND_PORT}" --listen-port "${PROXY_PORT}" >> /home/lmo/server_proxy_switch.log 2>&1 &
echo "Proxy started (logs: /home/lmo/server_proxy_switch.log)" | tee -a "${LOG_FILE}"

echo "Done. Use 'tail -F ${REPO_DIR}/server.log /home/lmo/server_proxy_switch.log ${LOG_FILE}' to follow logs." | tee -a "${LOG_FILE}"

echo "=== $(date -u +'%Y-%m-%dT%H:%M:%SZ') Finished run_backend_and_proxy.sh ===" >> "${LOG_FILE}"
