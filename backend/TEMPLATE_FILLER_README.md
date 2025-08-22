Template Filler for Mercado Libre (ML Mapper)
=============================================

Purpose
-------
This module implements a safe filler for Mercado Libre templates that preserves the
first 7 rows (header, instructions, formats, formulas) and writes product rows
starting at row 8 (Excel 1-based indexing). It ensures the original template's
formatting and layout remain intact.

Files added
-----------
- `src/template_filler.py`: core utilities implemented with openpyxl.

Key functions
-------------
- `preserve_template_header(workbook, header_rows=7)`
  - Semantically marks the header rows that must not be modified. The filling logic
    enforces this by writing only from `start_row` onward.

- `detect_columns(sheet, header_row=8)`
  - Scans the given header row (1-based) and tries to match logical fields (title,
    sku, price, shipping, stock, condition, images) to sheet column positions. It
    returns a mapping of logical field -> 1-based column index.

- `fill_products_from_row(sheet, start_row=8, products_data, default_values, overwrite=False)`
  - Writes products sequentially starting at `start_row`.
  - Will not overwrite existing cells unless `overwrite=True`.
  - Uses `default_values` for missing fields when available.
  - Returns detailed per-row filled/skipped logs suitable for reporting.

- `generate_fill_report(products_data, filled_columns, skipped_columns)`
  - Creates a concise summary report with counts and details per product.

Usage example (Python)
----------------------
from openpyxl import load_workbook
from src.template_filler import detect_columns, fill_products_from_row, generate_fill_report

wb = load_workbook('plantilla_ml.xlsx')
ws = wb.active

# Detect mapping from header row 8
mapping = detect_columns(ws, header_row=8)
print('Detected mapping:', mapping)

products = [
    {'title': 'Zapato rojo', 'sku': 'ZAP123', 'price': '45.50'},
    {'title': 'Remera blanca', 'sku': 'REM456', 'price': '25'}
]

# Defaults set by the wizard, applied if user didn't provide value for a field
defaults = {'condition': 'Nuevo', 'stock': 1, 'shipping': 'me2'}

filled, skipped = fill_products_from_row(ws, start_row=8, products_data=products, default_values=defaults, overwrite=False)
report = generate_fill_report(products, filled, skipped)
print(report)

# Save to new file, preserving original template except for rows >= 8
wb.save('plantilla_filled.xlsx')

Notes
-----
- The module uses simple substring matching for header detection; expand `HEADER_KEYWORDS`
  if your template uses other labels.
- The functions intentionally avoid touching rows 1..7. If you need to support templates
  where headers are not exactly at row 8, call `detect_columns` with the appropriate header row.

