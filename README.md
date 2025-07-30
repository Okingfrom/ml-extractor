# ML Extrator

A modular Python tool for extracting product data from various file formats (Excel, TXT, DOCX, PDF), mapping it to Mercado Libre's bulk upload template, and exporting the result.

## Features
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
3. Run the CLI:
   ```bash
   python main.py --help
   ```

## Project Structure
- `src/` - Source code modules
- `samples/` - Example input files and templates
- `config/` - Mapping and configuration files
- `.github/` - Copilot instructions and project docs

---
For more details, see the roadmap and code comments.
