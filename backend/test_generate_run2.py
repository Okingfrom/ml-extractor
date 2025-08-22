import asyncio
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import dev_server as ds

async def run_test():
    basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'samples'))
    ml_template_path = os.path.join(basedir, 'plantilla_ml_ejemplo.xlsx')
    product_path = os.path.join(basedir, 'productos_muestra.csv')

    # Build UploadFile-like objects
    from starlette.datastructures import UploadFile as StarletteUploadFile
    from io import BytesIO
    ml_data = open(ml_template_path, 'rb').read()
    prod_data = open(product_path, 'rb').read()
    ml_file = StarletteUploadFile(filename=os.path.basename(ml_template_path), file=BytesIO(ml_data))
    prod_file = StarletteUploadFile(filename=os.path.basename(product_path), file=BytesIO(prod_data))

    # Inspect CSV columns
    import pandas as pd
    df = pd.read_csv(product_path)
    print('Product CSV columns:', list(df.columns))

    # Correct mapping: ML template fields -> CSV column names
    mapping = {
        'Título': 'Nombre',
        'Precio': 'Precio',
        'Stock': 'Stock'
    }
    defaults = {
        'condition': 'new',
        'currency': 'ARS',
        'free_shipping': 'no',
        'accepts_mercado_pago': 'yes',
        'pickup_allowed': 'no',
        'default_stock': 1
    }

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
