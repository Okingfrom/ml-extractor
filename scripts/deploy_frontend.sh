#!/usr/bin/env bash
# Simple local build + rsync deploy script for the frontend
# Edit SERVER_USER, SERVER_HOST, TARGET_PATH to match your server.

set -euo pipefail

# Configuration - edit before running
SERVER_USER="youruser"
SERVER_HOST="yourserver.example"
TARGET_PATH="/home/youruser/public_html/extractorml.uy"
FRONTEND_DIR="frontend"
BUILD_DIR="build" # for create-react-app; change to dist for other frameworks

# Build
echo "Building frontend in ${FRONTEND_DIR}..."
cd "${FRONTEND_DIR}"
if [ -f package-lock.json ]; then
  npm ci
else
  npm install
fi
npm run build
cd -

# Deploy
echo "Rsyncing ${FRONTEND_DIR}/${BUILD_DIR}/ to ${SERVER_USER}@${SERVER_HOST}:${TARGET_PATH}/"
rsync -avz --delete "${FRONTEND_DIR}/${BUILD_DIR}/" "${SERVER_USER}@${SERVER_HOST}:${TARGET_PATH}/"

echo "Upload complete. Ensure ${TARGET_PATH}/.htaccess contains the proxy rules (deploy/frontend.htaccess)."
