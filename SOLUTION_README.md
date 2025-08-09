# ML Extractor - Working Solutions for Older CPUs

## Problem Resolution

Your original Streamlit app was experiencing "Illegal instruction (core dumped)" errors because:

1. **CPU Compatibility**: Your AMD A6-3400M processor doesn't support newer instruction sets (AVX, SSE4.2, etc.) required by modern NumPy/Pandas packages
2. **Dependencies**: Streamlit requires NumPy and Pandas, which are compiled with newer CPU instruction sets

## Working Solutions

### 1. Flask Web Application (Recommended)
**File**: `app_flask.py`
- Web interface similar to Streamlit but without NumPy/Pandas dependencies
- Uses pure Python with openpyxl for Excel handling
- Accessible at http://localhost:5000

**To run**:
```bash
source venv_flask/bin/activate
python app_flask.py
```

### 2. Command Line Version
**File**: `main_simple.py`
- Simple command-line interface
- No web dependencies

**To run**:
```bash
source venv_flask/bin/activate
python main_simple.py input_file.xlsx output_file.xlsx --config config/mapping.yaml
```

## Installation

1. Create virtual environment:
```bash
python3 -m venv venv_flask
source venv_flask/bin/activate
```

2. Install dependencies:
```bash
pip install flask openpyxl python-docx PyPDF2 PyYAML
```

## Features

Both solutions support:
- Excel (.xlsx, .xls) files
- CSV files  
- PDF files
- DOCX files
- Text files
- YAML configuration mapping
- Web interface (Flask version only)

## File Processing

The applications read your input files and map them according to the configuration in `config/mapping.yaml`, then output a properly formatted Excel file for Mercado Libre.

Both versions work without requiring NumPy, Pandas, or Streamlit, making them compatible with older CPU architectures.
