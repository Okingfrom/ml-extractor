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
