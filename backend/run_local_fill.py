"""Local runner to test template_filler without running the HTTP server.

This script:
- loads samples/sample_input.xlsx
- reads samples/productos_prueba_preview.csv
- maps fields using a simple mapping
- fills the template from row 8 and saves the output under uploads/
- prints a JSON fill report
"""
import sys
import os
import json
from datetime import datetime

# ensure src is importable
SRC = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
if SRC not in sys.path:
    sys.path.insert(0, SRC)

try:
    from template_filler import detect_columns, fill_products_from_row, generate_fill_report
except ImportError as e:
    print('Failed to import template_filler:', e)
    raise

import pandas as pd
from openpyxl import load_workbook

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
ML_TEMPLATE = os.path.join(BASE, 'samples', 'plantilla_ml_ejemplo.xlsx')
PRODUCTS_CSV = os.path.join(BASE, 'samples', 'productos_prueba_preview.csv')

if not os.path.exists(ML_TEMPLATE):
    print('ML template not found:', ML_TEMPLATE)
    sys.exit(1)
if not os.path.exists(PRODUCTS_CSV):
    print('Products CSV not found:', PRODUCTS_CSV)
    sys.exit(1)

# Simple mapping like the wizard would provide
mapping = {"title": "nombre", "price": "precio", "stock": "stock", "description": "descripcion"}
settings = {"condition": "new", "currency": "ARS", "free_shipping": "no", "accepts_mercado_pago": "yes", "pickup_allowed": "no", 'default_stock': 1}

print('Loading product data...')
df = pd.read_csv(PRODUCTS_CSV)

# Build products_data
products_data = []
for _, row in df.iterrows():
    prod = {}
    for ml_field, prod_field in mapping.items():
        try:
            if prod_field in row and pd.notna(row[prod_field]):
                val = row[prod_field]
                key = ml_field.lower()
                if 'titul' in key or 'title' in key or 'nombre' in key:
                    prod['title'] = val
                elif 'sku' in key:
                    prod['sku'] = val
                elif 'precio' in key or 'price' in key:
                    prod['price'] = val
                elif 'stock' in key or 'cantidad' in key:
                    prod['stock'] = val
                elif 'descrip' in key or 'description' in key:
                    prod['description'] = val
                else:
                    prod[ml_field] = val
        except Exception:
            continue
    products_data.append(prod)

print('Loaded', len(products_data), 'products')

# Load workbook and sheet
wb = load_workbook(ML_TEMPLATE)
ws = wb.active
HEADER_ROW = 1

# default values
default_values = {}
if 'condition' in settings:
    condition_map = {'new': 'Nuevo', 'used': 'Usado', 'refurbished': 'Reacondicionado'}
    default_values['condition'] = condition_map.get(settings['condition'], 'Nuevo')
if settings.get('free_shipping') in ('yes', True):
    default_values['shipping'] = 'me2'
if 'default_stock' in settings:
    default_values['stock'] = settings['default_stock']
else:
    default_values.setdefault('stock', 1)

print('Detected default values:', default_values)

filled_report, skipped_report = fill_products_from_row(ws, start_row='auto', products_data=products_data, default_values=default_values, overwrite=False)

report = generate_fill_report(products_data, filled_report, skipped_report)

# Save output workbook
os.makedirs(os.path.join(BASE, 'uploads'), exist_ok=True)
output_filename = f"ml_productos_mapeados_local_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
output_path = os.path.join(BASE, 'uploads', output_filename)
wb.save(output_path)

print('Saved generated file to', output_path)
print('Fill report:')
print(json.dumps(report, indent=2, ensure_ascii=False))
