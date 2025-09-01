#!/usr/bin/env python3
"""
Small runner script to start the simple FastAPI backend using Uvicorn.
This file is intended to be bundled with PyInstaller into a single executable.

Usage (after building):
  ./ml_extractor --host 0.0.0.0 --port 8000

Note: The runner imports `simple_backend.app` which keeps the project self-contained
for the purposes of packaging. If you need the full backend with SQLAlchemy, pack
`backend.main:app` instead and ensure its dependencies are available.
"""
import os
import argparse
import threading
import webbrowser
import time

try:
    # Try to import uvicorn programmatically
    import uvicorn
except Exception:
    uvicorn = None

# Import the ASGI app from the simple backend entrypoint
from simple_backend import app


def main():
    parser = argparse.ArgumentParser(description="Run ML Extractor simple backend (bundled)")
    parser.add_argument("--host", default=os.environ.get("HOST", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.environ.get("PORT", "8000")))
    parser.add_argument("--log-level", default=os.environ.get("LOG_LEVEL", "info"))
    args = parser.parse_args()

    if uvicorn is None:
        print("uvicorn is not available. Please install uvicorn or build with it included.")
        return

    # Function to run the server
    def run_server():
        uvicorn.run(app, host=args.host, port=args.port, log_level=args.log_level)

    # Start server in a thread
    thread = threading.Thread(target=run_server, daemon=True)
    thread.start()

    # Wait for server to start
    time.sleep(2)

    # Open browser to the frontend
    browser_host = "127.0.0.1" if args.host == "0.0.0.0" else args.host
    url = f"http://{browser_host}:{args.port}/"
    webbrowser.open(url)

    print(f"Server running at {url}. Press Ctrl+C to stop.")

    # Keep the main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping server...")


if __name__ == '__main__':
    main()
