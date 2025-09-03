Frontend and Backend entrypoints

This file defines the canonical frontend and backend entrypoints for the ML Extractor project. Keep this file in `main` and any active deployment branches.

- Frontend: `frontend/` (source)
  - Build output: `frontend/dist/`
  - Static entry served at domain root (`/`) by the chosen static hosting or by the backend staticfiles mount.

- Backend: `backend/` (FastAPI app)
  - Main ASGI app: `backend/main.py` (or `simple_backend.py` for single-file deployments)
  - Health endpoint: `/api/health`
  - Static files fallback: backend should only mount static files after API routes to avoid shadowing.

Notes:
- For Render/Docker deployments, use the Dockerfile in branch `pyinstaller-artifacts` which builds frontend and runs the backend on port 8000.
- For cPanel/Passenger deployments, `passenger_wsgi.py` is the startup file and should delegate to `backend/main.py` or `simple_backend.py`.

If you change entrypoints, update this file and any `.cpanel.yml` or `render.yaml` accordingly.
