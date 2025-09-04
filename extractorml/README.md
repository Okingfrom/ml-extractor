ExtractorML All-in-One

This branch bundles the FastAPI backend and React frontend into a single deployable app for quick testing.

Structure

extractorml/
├── backend/
│   ├── main.py
│   ├── requirements.txt
├── frontend/
│   ├── package.json
│   ├── src/
│   └── build/     # React build output
├── start.sh

How it works

- Backend serves API under `/api/*`.
- Backend serves React build (frontend/build or frontend/dist) as static files at `/`.
- Start app with `./start.sh` or `uvicorn backend.main:app --host 0.0.0.0 --port 8000`.

Deployment notes

- The app listens on port 8000 to satisfy single-port hosting.
- Use the provided Nginx block to proxy to 127.0.0.1:8000.

