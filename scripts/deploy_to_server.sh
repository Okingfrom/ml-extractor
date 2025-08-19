#!/usr/bin/env bash
set -euo pipefail

# deploy_to_server.sh
# Minimal deployment script to clone/pull the repo, create a venv, install
# dependencies and start the app with gunicorn (nohup). Designed for simple
# hosting environments (cPanel terminals or SSH access).
#
# Usage: ./deploy_to_server.sh [DEPLOY_DIR] [BRANCH]
# Example: ./deploy_to_server.sh ~/app_ml_extractor main

DEPLOY_DIR=${1:-"$HOME/app_ml_extractor"}
BRANCH=${2:-main}
REPO_URL=${REPO_URL:-"git@github.com:Okingfrom/ml-extractor.git"}
PYTHON_BIN=${PYTHON_BIN:-python3}

echo "Deploying ml-extractor to: $DEPLOY_DIR (branch: $BRANCH)"

# Create folder if needed
mkdir -p "$DEPLOY_DIR"
cd "$DEPLOY_DIR"

if [ ! -d .git ]; then
  echo "Cloning repository..."
  git clone --depth 1 --branch "$BRANCH" "$REPO_URL" .
else
  echo "Fetching latest..."
  git fetch origin "$BRANCH"
  git reset --hard "origin/$BRANCH"
fi

echo "Setting up virtualenv (.venv)..."
$PYTHON_BIN -m venv .venv
source .venv/bin/activate
pip install --upgrade pip setuptools wheel

if [ -f requirements.txt ]; then
  echo "Installing requirements..."
  pip install -r requirements.txt || echo "pip install reported errors; check logs"
else
  echo "No requirements.txt found. Skipping pip install."
fi

echo "Ensuring uploads and backups exist and are writable..."
mkdir -p uploads backups
chmod 750 uploads backups || true

if [ ! -f .env ]; then
  if [ -f .env.template ]; then
    echo "Creating .env from .env.template (please edit values)"
    cp .env.template .env
  else
    echo "No .env or .env.template found — create .env with SECRET_KEY and other variables before starting."
  fi
fi

echo "Stopping any previous gunicorn process (best-effort)..."
pkill -f 'gunicorn' || true

echo "Restarting systemd service 'ml-extractor' so systemd manages the process (no manual nohup)."
# if systemd is available and the unit exists, restart it; otherwise fall back to a local nohup
if command -v systemctl >/dev/null 2>&1 && [ -f /etc/systemd/system/ml-extractor.service ]; then
  echo "Systemd unit found — restarting ml-extractor.service"
  sudo systemctl daemon-reload || true
  sudo systemctl restart ml-extractor.service || {
    echo "systemctl restart failed — falling back to launching gunicorn directly"
    nohup .venv/bin/gunicorn -b 127.0.0.1:8000 app_improved:app --workers 3 --timeout 120 > gunicorn.log 2>&1 &
  }
else
  echo "No systemd unit found — starting gunicorn with nohup"
  nohup .venv/bin/gunicorn -b 127.0.0.1:8000 app_improved:app --workers 3 --timeout 120 > gunicorn.log 2>&1 &
fi

echo "Deploy finished. Check gunicorn.log for output and errors."
echo "If your hosting requires a different startup (Passenger/Apache), adapt the command accordingly."

echo "Recommended next steps:"
echo " - Configure reverse proxy or Application Manager to expose 127.0.0.1:8000 to your domain." 
echo " - Configure environment variables (SECRET_KEY, DATABASE_URL, etc.) in hosting control panel." 
#!/usr/bin/env bash
set -euo pipefail

# deploy_to_server.sh
# Minimal deployment script to clone/pull the repo, create a venv, install
# dependencies and start the app with gunicorn (nohup). Designed for simple
# hosting environments (cPanel terminals or SSH access).
#
# Usage: ./deploy_to_server.sh [DEPLOY_DIR] [BRANCH]
# Example: ./deploy_to_server.sh ~/app_ml_extractor main

DEPLOY_DIR=${1:-"$HOME/app_ml_extractor"}
BRANCH=${2:-main}
REPO_URL=${REPO_URL:-"git@github.com:Okingfrom/ml-extractor.git"}
PYTHON_BIN=${PYTHON_BIN:-python3}

echo "Deploying ml-extractor to: $DEPLOY_DIR (branch: $BRANCH)"

# Create folder if needed
mkdir -p "$DEPLOY_DIR"
cd "$DEPLOY_DIR"

if [ ! -d .git ]; then
  echo "Cloning repository..."
  git clone --depth 1 --branch "$BRANCH" "$REPO_URL" .
else
  echo "Fetching latest..."
  git fetch origin "$BRANCH"
  git reset --hard "origin/$BRANCH"
fi

echo "Setting up virtualenv (.venv)..."
$PYTHON_BIN -m venv .venv
source .venv/bin/activate
pip install --upgrade pip setuptools wheel

if [ -f requirements.txt ]; then
  echo "Installing requirements..."
  pip install -r requirements.txt || echo "pip install reported errors; check logs"
else
  echo "No requirements.txt found. Skipping pip install."
fi

echo "Ensuring uploads and backups exist and are writable..."
mkdir -p uploads backups
chmod 750 uploads backups || true

if [ ! -f .env ]; then
  if [ -f .env.template ]; then
    echo "Creating .env from .env.template (please edit values)"
    cp .env.template .env
  else
    echo "No .env or .env.template found — create .env with SECRET_KEY and other variables before starting."
  fi
fi

echo "Stopping any previous gunicorn process (best-effort)..."
pkill -f 'gunicorn' || true

echo "Starting gunicorn (nohup) on 127.0.0.1:8000 — adjust as needed for cPanel proxy/ports"
nohup .venv/bin/gunicorn -b 127.0.0.1:8000 app_improved:app \
  --workers 3 --timeout 120 > gunicorn.log 2>&1 &

echo "Deploy finished. Check gunicorn.log for output and errors."
echo "If your hosting requires a different startup (Passenger/Apache), adapt the command accordingly."

echo "Recommended next steps:"
echo " - Configure reverse proxy or Application Manager to expose 127.0.0.1:8000 to your domain." 
echo " - Configure environment variables (SECRET_KEY, DATABASE_URL, etc.) in hosting control panel." 
