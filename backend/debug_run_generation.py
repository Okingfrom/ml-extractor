import pandas as pd
import os, json, traceback

ml_path = r'C:\Users\equipo\Desktop\ml-extractor\samples\sample_input.xlsx'
prod_path = r'C:\Users\equipo\Desktop\ml-extractor\samples\productos_prueba_preview.csv'

mapping = {"title": "nombre", "price": "precio", "stock": "stock", "description": "descripcion"}
settings = {"condition": "new", "currency": "ARS", "free_shipping": "no", "accepts_mercado_pago": "yes", "pickup_allowed": "no"}

try:
    ml_df = pd.read_excel(ml_path, header=None)
    product_df = pd.read_csv(prod_path)

    # find data_start_row
    data_start_row = 8
    for i in range(min(15, len(ml_df))):
        row = ml_df.iloc[i]
        non_null_count = row.count()
        if non_null_count >= len(ml_df.columns) * 0.5:
            data_start_row = i
            break

    print('data_start_row=', data_start_row)

    # Our in-memory building logic
    min_expected_cols = 12
    num_cols = max(len(ml_df.columns), min_expected_cols)
    print('num_cols=', num_cols, 'ml_df.columns=', len(ml_df.columns))

    def normalize_row_list(row_list):
        row = list(row_list) if row_list is not None else []
        if len(row) < num_cols:
            row = row + [None] * (num_cols - len(row))
        elif len(row) > num_cols:
            row = row[:num_cols]
        return row

    header_rows = [normalize_row_list(ml_df.iloc[i].tolist()) for i in range(min(data_start_row, len(ml_df)))]
    if data_start_row < len(ml_df):
        base_template_row = normalize_row_list(ml_df.iloc[data_start_row].tolist())
    else:
        base_template_row = [None] * num_cols
    footer_rows = []
    if data_start_row + 1 < len(ml_df):
        footer_rows = [normalize_row_list(ml_df.iloc[i].tolist()) for i in range(data_start_row + 1, len(ml_df))]

    col_idx = {
        'title': 1,
        'price': 2,
        'stock': 3,
        'category': 4,
        'condition': 5,
        'currency': 6,
        'free_shipping': 7,
        'accepts_mercado_pago': 8
    }

    data_rows = []
    for product_idx, product_row in product_df.iterrows():
        out_row = base_template_row.copy()
        for ml_field, product_field in mapping.items():
            try:
                if product_field in product_row and pd.notna(product_row[product_field]):
                    value = product_row[product_field]
                else:
                    continue
            except Exception:
                continue
            key = ml_field.lower()
            if 'título' in key or 'title' in key:
                idx = col_idx['title']
                if idx < num_cols:
                    out_row[idx] = value
            elif 'precio' in key or 'price' in key:
                idx = col_idx['price']
                if idx < num_cols:
                    out_row[idx] = value
            elif 'stock' in key:
                idx = col_idx['stock']
                if idx < num_cols:
                    out_row[idx] = value
            elif 'categor' in key or 'category' in key:
                idx = col_idx['category']
                if idx < num_cols:
                    out_row[idx] = value
        if settings:
            if 'condition' in settings:
                idx = col_idx['condition']
                if idx < num_cols:
                    out_row[idx] = {'new':'Nuevo','used':'Usado','refurbished':'Reacondicionado'}.get(settings['condition'],'Nuevo')
            if 'currency' in settings:
                idx = col_idx['currency']
                if idx < num_cols:
                    out_row[idx] = settings['currency']
            if 'free_shipping' in settings:
                idx = col_idx['free_shipping']
                if idx < num_cols:
                    out_row[idx] = 'Sí' if settings['free_shipping']=='yes' else 'No'
            if 'accepts_mercado_pago' in settings:
                idx = col_idx['accepts_mercado_pago']
                if idx < num_cols:
                    out_row[idx] = 'Sí' if settings['accepts_mercado_pago']=='yes' else 'No'
        data_rows.append(out_row)

    final_rows = []
    final_rows.extend(header_rows)
    final_rows.extend(data_rows)
    final_rows.extend(footer_rows)

    output_df = pd.DataFrame(final_rows, columns=list(range(num_cols)))
    out_path = os.path.join('..','uploads','debug_generated.xlsx')
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    output_df.to_excel(out_path, index=False, header=False)
    print('Generated file at', out_path)

except Exception as e:
    print('Exception:', str(e))
    traceback.print_exc()

print('Done')
