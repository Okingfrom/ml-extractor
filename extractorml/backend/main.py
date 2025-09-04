from fastapi import FastAPI, APIRouter, Request
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI(title="ExtractorML - All-in-One")
api = APIRouter(prefix="/api")

@api.get("/health")
async def health():
    return {"status": "healthy", "service": "extractorml", "version": "1.0"}

# Example API route
@api.get("/hello")
async def hello():
    return {"message": "Hello from ExtractorML API"}

app.include_router(api)

# Determine frontend build path (support frontend/build or frontend/dist)
HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(HERE, '..'))
CANDIDATES = [
    os.path.join(REPO_ROOT, '..', 'frontend', 'build'),
    os.path.join(REPO_ROOT, '..', 'frontend', 'dist'),
    os.path.join(REPO_ROOT, '..', 'frontend', 'frontend', 'build'),
]
FRONTEND_PATH = None
for p in CANDIDATES:
    if os.path.isdir(p):
        FRONTEND_PATH = p
        break

if FRONTEND_PATH:
    # Mount static files under root
    app.mount("/static", StaticFiles(directory=os.path.join(FRONTEND_PATH, 'static')), name="static")

    @app.get("/", response_class=HTMLResponse)
    async def root_index():
        index = os.path.join(FRONTEND_PATH, 'index.html')
        if os.path.exists(index):
            return FileResponse(index, media_type='text/html')
        return HTMLResponse("<html><body><h1>Frontend build not found</h1></body></html>")

    # Fallback for SPA routes
    @app.get("/{full_path:path}", response_class=HTMLResponse)
    async def spa_fallback(full_path: str, request: Request):
        # avoid intercepting API routes
        if request.url.path.startswith('/api/'):
            return JSONResponse({"detail": "Not found"}, status_code=404)
        index = os.path.join(FRONTEND_PATH, 'index.html')
        if os.path.exists(index):
            return FileResponse(index, media_type='text/html')
        return JSONResponse({"detail": "Frontend not built"}, status_code=404)
else:
    @app.get("/", response_class=HTMLResponse)
    async def root_no_frontend():
        return HTMLResponse("<html><body><h1>No frontend build found (run npm run build)</h1></body></html>")

if __name__ == '__main__':
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, log_level="info")
