import asyncio
import json
import os
import sys
from fastapi import UploadFile
from io import BytesIO

sys.path.insert(0, os.path.dirname(__file__))
import dev_server as ds

# Helper to create a FastAPI UploadFile from a local file
async def make_uploadfile(path, filename=None):
    if filename is None:
        filename = os.path.basename(path)
    data = open(path, 'rb').read()
    # Simulate UploadFile using starlette.datastructures.UploadFile? We'll use FastAPI UploadFile interface via BytesIO
    from starlette.datastructures import UploadFile as StarletteUploadFile
    b = BytesIO(data)
    su = StarletteUploadFile(filename=filename, file=b)
    return su

async def run_test():
    basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'samples'))
    ml_template_path = os.path.join(basedir, 'plantilla_ml_ejemplo.xlsx')
    product_path = os.path.join(basedir, 'productos_muestra.csv')

    ml_file = await make_uploadfile(ml_template_path)
    prod_file = await make_uploadfile(product_path)

    # Simple mapping: map source CSV columns to ML fields
    # We'll inspect the CSV headers quickly
    import pandas as pd
    df = pd.read_csv(product_path)
    print('Product CSV columns:', list(df.columns))

    # naive mapping assuming CSV has 'title','price','stock'
    mapping = {
        'Título': 'title',
        'Precio': 'price',
        'Stock': 'stock'
    }
    defaults = {
        'condition': 'new',
        'currency': 'ARS',
        'free_shipping': 'no',
        'accepts_mercado_pago': 'yes',
        'pickup_allowed': 'no',
        'default_stock': 1
    }

    # Call the handler directly
    try:
        resp = await ds.generate_ml_file_endpoint(
            ml_template=ml_file,
            product_data=prod_file,
            mapping_config=json.dumps(mapping, ensure_ascii=False),
            default_settings=json.dumps(defaults, ensure_ascii=False),
            write_mode='fill-empty',
            edits=None
        )
        print(json.dumps(resp, ensure_ascii=False, indent=2))
    except Exception as e:
        import traceback
        print('Error calling generate_ml_file_endpoint:', str(e))
        traceback.print_exc()

if __name__ == '__main__':
    asyncio.run(run_test())
