#!/bin/bash
# Build PyInstaller executable for Ubuntu/Linux
# Run this on an Ubuntu machine with Python 3.8+ and venv

echo "Building PyInstaller executable for Ubuntu..."

# Install dependencies if not already
pip install pyinstaller uvicorn fastapi pydantic python-decouple

# Build the executable
pyinstaller --onefile run_simple_backend.py

echo "Build complete! Executable at dist/run_simple_backend"
echo "To run: ./dist/run_simple_backend"
