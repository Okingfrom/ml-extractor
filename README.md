# ML Extractor - AI-Powered Mercado Libre Bulk Mapper 🚀

A sophisticated Python application that intelligently maps product data from various file formats to Mercado Libre's bulk upload template, enhanced with AI capabilities for automatic data completion.

## ✨ Features

### 🧠 AI-Powered Enhancement
- **Smart brand detection** from product names and descriptions
- **Automatic model/SKU generation** based on product information  
- **Realistic weight estimation** by product category
- **Color inference** from product descriptions
- **Standard warranty assignment** by product type
- **Valid EAN-13 code generation**

### 🌐 Professional Web Interface
- Modern Flask-based web application
- Professional Mercado Libre themed design
- Real-time processing feedback
- Comprehensive debug logging
- Intuitive file upload and field mapping

### 📁 Multi-Format Support
- Modular file readers for Excel, TXT, DOCX, and PDF
- Configuration-driven data mapping
- CLI entry point for automation and scripting
- Logging and validation
- Sample data and configuration folders
- Ready for future extensibility (e.g., web UI)

## Quick Start
1. Set up a Python virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   (For development/testing use the extended set)
   ```bash
   pip install -r requirements-dev.txt
   ```
3. Run the CLI:
   ```bash
   python main.py --help
   ```
      git remote remove origin  # Only if you already have an 'origin' set
   git remote add origin https://github.com/Okingfrom/ml-extrator.git
   git branch -M main
   git push -u origin main   git remote remove origin  # Only if you already have an 'origin' set
   git remote add origin https://github.com/Okingfrom/ml-extrator.git
   git branch -M main
   git push -u origin main   sudo apt install python3-venv python3-pip

## Project Structure
- `src/` - Source code modules
- `samples/` - Example input files and templates
- `config/` - Mapping and configuration files
- `.github/` - Copilot instructions and project docs
- `frontend/` - React (SPA) source (optional UI layer)

## 🖥 React Frontend Integration (Optional)
The project can serve a React single-page application. Two modes:

1. Legacy Flask Template (default): Inline HTML/CSS served from `app_improved.py`.
2. React SPA: Build the frontend and let Flask serve the static bundle.

### Enable React UI
1. Install frontend dependencies:
   ```bash
   cd frontend
   npm install
   npm run build
   cd ..
   ```
2. Run backend with React mode:
   ```bash
   USE_REACT_UI=1 python3 app_improved.py
   ```
3. (Dev hot reload) In one terminal run `npm start` (or Vite dev), in another run:
   ```bash
   ML_EXTRACTOR_DEV=1 USE_REACT_UI=1 python3 app_improved.py
   ```

### API Notes
- Health endpoint: `GET /api/health` returns `{ status, react, dev }`.
- Add new JSON endpoints under `/api/`.
- CORS enabled in dev (`ML_EXTRACTOR_DEV=1` & `USE_REACT_UI=1`).

### Environment Flags
- `ML_EXTRACTOR_DEV=1` enables developer utilities & CORS.
- `USE_REACT_UI=1` switches to serving the React build (fallback to legacy if missing build).

### Future Split
Keep back-end routes pure JSON and avoid embedding UI state server-side to simplify extracting `frontend/` to its own repo or deploying via CDN.

---
For more details, see the roadmap and code comments.

## Admin API & Remote Backend

The backend now exposes a small admin API to manage provider API keys and application settings:

- GET /api/admin/settings  - returns masked settings (admin only)
- POST /api/admin/settings - create/update a provider setting {provider, api_key, notes} (admin only)
- DELETE /api/admin/settings/{provider} - remove a provider setting (admin only)

The frontend `Admin Settings` page (Development route: `/admin/settings`) uses these endpoints.

Pointing the frontend to a remote backend:

- In development, the frontend uses `frontend/src/services/api.js` which defaults to `http://localhost:8010`.
- To point the frontend at a remote backend (for testing), update the `baseURL` in `frontend/src/services/api.js` or set the appropriate environment variable when building the frontend.

Security note: This admin API is a minimal developer convenience. For production, store API keys and private credentials in a secure vault (Cloud Secret Manager), use encrypted storage, and protect the admin endpoints with strong authentication and role-based access control.

## Run locally with Docker (backend + frontend)

We provide a `docker-compose.yml` that builds and runs both the backend (FastAPI) and the frontend (React served by nginx) together.

1. Install Docker Desktop (Windows) and enable WSL2 integration if available.
2. From the project root, build and run:

```powershell
docker compose up --build
```

3. The frontend will be available at http://localhost:3000 and the backend API at http://localhost:8010.

4. To pass an OpenAI API key for local testing, set environment variable before running:

```powershell
$env:OPENAI_API_KEY = "sk-..."
docker compose up --build
```

To stop and remove containers:

```powershell
docker compose down
```

