import os
import sys
import json
from datetime import datetime
import pandas as pd

# Ensure src is importable
SRC = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from template_filler import fill_products_from_row, generate_fill_report, detect_columns

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
SAMPLES = os.path.join(REPO, 'samples')
UPLOADS = os.path.join(REPO, 'uploads')
os.makedirs(UPLOADS, exist_ok=True)

ml_path = os.path.join(SAMPLES, 'sample_input.xlsx')
prod_path = os.path.join(SAMPLES, 'productos_prueba_preview.csv')

mapping = {"title": "nombre", "price": "precio", "stock": "stock", "description": "descripcion"}
settings = {"condition": "new", "currency": "ARS", "free_shipping": "no", "accepts_mercado_pago": "yes", "pickup_allowed": "no"}

print('Loading product data from', prod_path)
product_df = pd.read_csv(prod_path)

# Build products_data list
products_data = []
for _, product_row in product_df.iterrows():
    prod = {}
    for ml_field, product_field in mapping.items():
        try:
            if product_field in product_row and pd.notna(product_row[product_field]):
                value = product_row[product_field]
            else:
                continue
        except Exception:
            continue
        key = ml_field.lower()
        if 'titul' in key or 'title' in key or 'nombre' in key:
            prod['title'] = value
        elif 'sku' in key:
            prod['sku'] = value
        elif 'precio' in key or 'price' in key:
            prod['price'] = value
        elif 'envio' in key or 'shipping' in key:
            prod['shipping'] = value
        elif 'stock' in key or 'cantidad' in key:
            prod['stock'] = value
        elif 'cond' in key or 'condition' in key:
            prod['condition'] = value
        elif 'image' in key or 'imagen' in key:
            prod['images'] = value
    products_data.append(prod)

print('Products parsed:', len(products_data))

# default values
default_values = {}
if settings:
    if 'condition' in settings:
        condition_map = {'new': 'Nuevo', 'used': 'Usado', 'refurbished': 'Reacondicionado'}
        default_values['condition'] = condition_map.get(settings['condition'], 'Nuevo')
    if settings.get('free_shipping') in ('yes', True):
        default_values['shipping'] = 'me2'
    if 'default_stock' in settings:
        default_values['stock'] = settings['default_stock']
    else:
        default_values.setdefault('stock', 1)

print('Default values:', default_values)

# Load workbook and sheet
from openpyxl import load_workbook
wb = load_workbook(ml_path)
ws = wb.active

# Run filler
filled_report, skipped_report = fill_products_from_row(ws, start_row=8, products_data=products_data, default_values=default_values, overwrite=False)

report = generate_fill_report(products_data, filled_report, skipped_report)
print('Fill report:')
print(json.dumps(report, indent=2, ensure_ascii=False))

# Save output
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
outfile = os.path.join(UPLOADS, f'ml_local_generated_{timestamp}.xlsx')
wb.save(outfile)
print('Saved generated file to', outfile)
