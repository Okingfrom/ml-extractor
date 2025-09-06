# ML Extractor - AI-Powered Mercado Libre Bulk Mapper 🚀

A sophisticated Python application that intelligently maps product data from various file formats to Mercado Libre's bulk upload template, enhanced with AI capabilities for automatic data completion.

## ✨ Features

## 🧠 AI-Powered Enhancement (Planned – Phase 4)

This project will optionally use AI to enrich MercadoLibre bulk listing templates. AI is NOT active yet; the baseline mapping and deterministic enrichment run without external models.

### What AI Will (Optionally) Do
| Capability | Description | Trigger | Safety Rule |
|------------|-------------|---------|-------------|
| Fill missing description | Generate coherent, category-aligned text | User enables "Generate descriptions" | No fabricated specs |
| Suggest attributes | Infer color, material, brand variants, etc. | User enables "Suggest attributes" | Only plausible inferences |
| Language adaptation | Adapt Spanish ↔ Portuguese (pt-BR) and regional Spanish variants | User selects target locale | Preserve original meaning |
| Enrich recommended fields | Add bullet points, extended marketing copy | User enables "Extended content" | Do not alter required validated fields |
| Consistency rewrite | Normalize titles (capitalization/style) | Always optional toggle | Do not remove key brand tokens |

### Required vs Recommended vs AI-Eligible

| Field Group | Examples | Status | AI Action |
|-------------|----------|--------|-----------|
| Required (never hallucinate) | título, categoría ID, precio, moneda, cantidad, condición | Must be present in source or validated mapping | AI may rephrase formatting only if explicitly allowed |
| Recommended | descripción, atributos adicionales, viñetas | Optional | AI may generate if toggle on |
| Derivable Attributes | color, material, marca (brand), peso estimado | Can be inferred | Provide confidence + mark uncertain values |
| Non-AI Fields (integrity) | SKU original, códigos internos, ID categoría, GTIN auto-validado | Integrity fields | Never generate or modify silently |

### High-Level Flow (MercadoLibre Bulk Import)
1. Subir archivo (CSV/XLSX/JSON)
2. Seleccionar plantilla de categoría (estructura oficial)
3. Mapear columnas origen → columnas plantilla
4. Validar campos obligatorios (no seguir si faltan)
5. (Opcional) Aplicar enriquecimiento AI
6. Generar archivo final / envío a API
7. Confirmar resultados y errores

### Planned Feature Flag
AI features will be behind:
```
ENABLE_AI=1
```
If unset, pipeline remains fully deterministic.

### Draft Internal AI System Prompt (Template)
```
You are an assistant enriching MercadoLibre bulk product template rows.
Rules:
- Do NOT fabricate category IDs, prices, SKU, or regulatory codes.
- Fill required fields ONLY if reliable source data exists.
- For descriptions: concise intro + bullet highlights (if requested).
- Mark uncertain attribute inferences with a confidence note (internal, not written to final cell).
- Language target: {{target_locale}} (e.g. es-AR, es-MX, pt-BR).
- Do not output JSON, only return field:value pairs with plain UTF-8 text where needed.
- Avoid repeating brand redundantly in every bullet.
Input context:
{{product_row}}
Required fields set: {{required_fields_present}}
Requested enrichment modes: {{enrichment_modes}}
Output only enriched fields (leave others untouched).
```

### Safety & Compliance Notes
- Never generate pricing strategy, tax statements, or regulatory claims.
- Avoid adding warranties unless explicitly provided.
- Strictly preserve sheet name "Publicaciones" and column ordering from official templates.

### Future Implementation Plan (Phase 4)
1. Add `src/ai/description_generator.py` with a single `generate_description(record, locale, modes, enable_ai)` function.
2. Integrate behind feature flag in mapper pipeline extension.
3. Add tests with a mock model (no external API first).
4. Introduce confidence metadata in `record["_meta"]["ai"]`.
5. Allow user toggles from UI later (Phase 2 extension after base API stable).

See: docs/AI_DESCRIPTION_ENRICHMENT.md for full specification (to be added).

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

## 🚀 API Usage (Phase 1)

### Starting the API Server
```bash
# Install dependencies (if not already installed)
pip install -r requirements.txt

# Start the API server (uvicorn already included in requirements.txt)
uvicorn src.api.app:app --reload --host 0.0.0.0 --port 8000
```

### API Endpoints

**Health Check**
```bash
curl http://localhost:8000/health
# Returns: {"status": "ok", "version": "1.0.0"}
```

**Map Single Record**
```bash
curl -X POST http://localhost:8000/map/single \
  -H "Content-Type: application/json" \
  -d '{"record": {"title": "Sony Headphones", "price": "99.99"}}'
```

**Map Multiple Records**
```bash
curl -X POST http://localhost:8000/map \
  -H "Content-Type: application/json" \
  -d '{"records": [{"title": "Sony Headphones", "price": "99.99"}, {"title": "Apple iPhone", "price": "699.99"}]}'
```

### Debug Logging
Enable detailed logging for development:
```bash
LOG_LEVEL=DEBUG uvicorn src.api.app:app --reload
```

### Error Handling
The API uses tolerant error handling:
- Empty payloads return empty results (200 status)
- Invalid record formats are coerced when possible
- Server errors return 500 with error details

### Type Checking
Static type checking is configured with Pyright in `pyrightconfig.json`:

```bash
# Install pyright (if not already installed)
npm install -g pyright

# Run type checking
pyright

# Alternative: use npx without global install
npx pyright
```

**Phase upgrade path**: The configuration starts with `standard` mode and gradually enables stricter checks:
- **Phase 1** (Current): `standard` mode with basic import/module checks
- **Phase 2**: Enable selective strict warnings for decorators and base classes  
- **Phase 3**: Full `strict` mode with complete type inference

Current configuration excludes `tests/` and focuses on `src/` directory only.

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

