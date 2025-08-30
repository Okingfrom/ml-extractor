This document outlines minimal steps to build and deploy the backend to Google Cloud Run.

Prerequisites:
- gcloud CLI installed and authenticated
- Docker installed (or use Cloud Build)

Steps:
1. Build the container image (locally):
   docker build -t gcr.io/PROJECT_ID/ml-extractor-api:latest .

2. Push to Google Container Registry (or Artifact Registry):
   docker push gcr.io/PROJECT_ID/ml-extractor-api:latest

3. Deploy to Cloud Run:
   gcloud run deploy ml-extractor-api --image gcr.io/PROJECT_ID/ml-extractor-api:latest --platform managed --region REGION --allow-unauthenticated --port 8010

Secrets & SSH keys:
- Do NOT bake secrets or private keys into the image. Use Cloud Secret Manager and mount them as environment variables or fetch at runtime.
- For SSH deployments, store private keys in Secret Manager and write them to a secure tmp path at runtime with strict permissions.

Configuration:
- The admin settings are stored in `config_admin.json` in the container's working directory in this simple implementation. For production, replace with a persistent store (Cloud SQL, Firestore, or Secret Manager) and encryption at rest.

Notes:
- The container runs `python simple_backend.py` which starts a uvicorn server bound to port 8010. Cloud Run respects container port mapping.
- Ensure your service account has permissions to access Secret Manager if secrets are used.
