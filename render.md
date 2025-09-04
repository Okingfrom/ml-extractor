# Deploying ml-extractor to Render (Docker)

This document describes a minimal, reproducible path to deploy the full app (backend + frontend) to Render using Docker. The repository already contains a `Dockerfile` that builds the frontend (if `frontend/package.json` exists) and the Python backend, and a `render.yaml` so Render can auto-detect services.

Prerequisites
- A Render account (https://render.com) with GitHub connected.
- Your repo is pushed to the branch `pyinstaller-artifacts` (we pushed the Dockerfile + render.yaml there).

High-level flow
1. In Render, create a new Web Service and choose Docker (Render will use the `Dockerfile` at the repo root).
2. Render will build the container using the Dockerfile and run the container. The container starts gunicorn with uvicorn workers and binds to the port Render provides.
3. The frontend is built during the Docker build step (if `frontend/package.json` exists) and the FastAPI app serves `frontend/dist` at `/`.

Render Docker UI steps (copy-paste friendly)
1. New -> Web Service
2. Select GitHub, pick repository `Okingfrom/ml-extractor` and branch `pyinstaller-artifacts`.
3. Choose "Docker" for the Environment.
4. Name: `ml-extractor` (or whatever you prefer).
5. Region/Plan: choose suitable region / free plan for testing.
6. Click Create Service. Render will read the `Dockerfile` from repo root and start a build.

Environment variables (set in Render service settings)
- SECRET_KEY (if your app uses one) — keep private.
- CORS_ORIGINS or CORS_ALLOWED_ORIGINS — add your frontend URL(s) or `*` for quick testing.
- Any other env your app expects (DB URLs, tokens). Use Render dashboard -> Environment -> Add Environment Variable.

Health check
- Configure a health check path in the Render service: `/api/health` (the backend already exposes this endpoint). Render will mark the service healthy/unhealthy based on that.

Local test commands (before pushing to Render)
- Build locally with Docker to catch build errors quickly:
```bash
# from repo root
docker build -t ml-extractor:local .
# run container, map host 8000 to container 8000
docker run --rm -p 8000:8000 ml-extractor:local
# then test
curl -v http://localhost:8000/api/health
curl -v http://localhost:8000/
```

If the local build fails with Python dependency errors (pip), inspect `requirements.txt` and the Docker build output for the failing package. Common fixes:
- Remove/replace problematic packages (for example `asgi2wsgi`) from `requirements.txt` if unused.
- Pin versions that are known to work with Python 3.10.

Troubleshooting notes (common issues on Render)
- Build fails installing a wheel or compiling a dependency:
  - Check build logs (Render provides the full Docker build output). If a binary dependency is missing, add the OS-level package to the Dockerfile (for example `libpq-dev` for PostgreSQL client libs).
- Frontend 404 at `/` after deploy:
  - Confirm `frontend/dist/index.html` exists in the built image. The Dockerfile builds `frontend/dist` if `frontend/package.json` exists; if your repo does not include frontend sources, add them or serve a committed `frontend/dist`.
- App import errors (ModuleNotFoundError) when starting gunicorn:
  - Ensure the start command matches your import path. We use `simple_backend:app`. If your app module is elsewhere, update CMD in the Dockerfile or `startCommand` in `render.yaml`.
- CORS errors from browser:
  - Add the frontend domain to `CORS_ORIGINS` and restart the service.

Using the existing `render.yaml`
- `render.yaml` already defines two services: a Python web service and a static site for the frontend. If you prefer Docker-only, select Docker when creating the web service and Render will use `Dockerfile` instead of the Python service config in `render.yaml`.

Custom domain (optional)
- In Render: Service -> Settings -> Custom Domains -> Add Custom Domain.
- Follow Render's DNS instructions (CNAME/A) in your DNS provider (cPanel). After DNS propagation, Render will issue TLS automatically.

What I pushed to `pyinstaller-artifacts`
- `Dockerfile` — builds frontend (if present) and backend, runs gunicorn with uvicorn workers.
- `.dockerignore` — reduces build context.
- `render.yaml` — contains both a web service and a static frontend service; Render can auto-create services from it.

If you hit a build error, paste the Render build log here and I will:
- suggest a small Dockerfile or requirements edit to fix the build, or
- produce a one-line fix (OS packages or pip pin) and push it to the branch.

If you want, I can also create a tiny GitHub Action to build and push the Docker image to GitHub Container Registry and then use that image on Render (advanced). Say "yes" and I’ll scaffold it.

Quick checklist to finish (you)
1. Open Render and create a Docker Web Service for `pyinstaller-artifacts` (use Docker option).
2. Add env vars required by the app (SECRET_KEY, CORS origins, etc.).
3. Watch build logs; if failing, paste them here.

Done.
