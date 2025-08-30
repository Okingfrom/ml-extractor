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
