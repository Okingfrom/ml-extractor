#!/usr/bin/env bash
set -euo pipefail

# Simple build script to create a one-file PyInstaller executable for run_simple_backend.py
# Run this on the target OS (build on Linux for Linux binaries). Requires PyInstaller and project deps.

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUTPUT_DIR="${PROJECT_DIR}/dist-pyinstaller"
RUNNER="${PROJECT_DIR}/run_simple_backend.py"

echo "Project dir: ${PROJECT_DIR}"

# Activate venv if present
if [ -f "${PROJECT_DIR}/.venv/bin/activate" ]; then
  source "${PROJECT_DIR}/.venv/bin/activate"
fi

# Ensure pyinstaller and uvicorn are installed
pip install --upgrade pip
pip install pyinstaller uvicorn

# Clean previous builds
rm -rf build dist ${OUTPUT_DIR}

# Build a onefile executable
pyinstaller --onefile --name ml_extractor \
  --add-data "frontend:frontend" \
  --add-data "deploy:deploy" \
  --hidden-import=uvicorn.main \
  "${RUNNER}"

# Move artifact to output dir
mkdir -p "${OUTPUT_DIR}"
mv dist/ml_extractor "${OUTPUT_DIR}/ml_extractor"

echo "Build complete: ${OUTPUT_DIR}/ml_extractor"
