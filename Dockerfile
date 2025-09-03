FROM python:3.10-slim

# Install Node (for building the frontend) and basic build tools
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl ca-certificates build-essential git \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy source
COPY . /app

# Build frontend if package.json exists
RUN if [ -f frontend/package.json ]; then \
      cd frontend && npm ci && npm run build && cd ..; \
    fi

# Install Python deps
RUN pip install --no-cache-dir -r requirements.txt

ENV PORT=8000
EXPOSE 8000

# Start using gunicorn with uvicorn workers
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "simple_backend:app", "--bind", "0.0.0.0:8000", "--log-level", "info"]
# Minimal Dockerfile for FastAPI backend (simple_backend.py)
# Build: docker build -t ml-extractor-api:latest .
# Run locally: docker run -p 8010:8010 ml-extractor-api:latest

FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . /app
EXPOSE 8010
CMD ["python", "simple_backend.py"]
