import requests
import json
import os

API = 'http://localhost:8009/api/files/generate-ml-file'
DOWNLOAD_BASE = 'http://localhost:8009'
ml_path = r'C:\Users\equipo\Desktop\ml-extractor\samples\sample_input.xlsx'
prod_path = r'C:\Users\equipo\Desktop\ml-extractor\samples\productos_prueba_preview.csv'

mapping = {"title": "nombre", "price": "precio", "stock": "stock", "description": "descripcion"}
settings = {"condition": "new", "currency": "ARS", "free_shipping": "no", "accepts_mercado_pago": "yes", "pickup_allowed": "no"}

files = {
    'ml_template': ('sample_input.xlsx', open(ml_path, 'rb'), 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
    'product_data': ('productos_prueba_preview.csv', open(prod_path, 'rb'), 'text/csv')
}

data = {
    'mapping_config': json.dumps(mapping),
    'default_settings': json.dumps(settings)
}

print('Sending generate request to', API)
resp = requests.post(API, files=files, data=data)

print('Status code:', resp.status_code)
try:
    res_json = resp.json()
    print(json.dumps(res_json, indent=2, ensure_ascii=False))
except Exception as e:
    print('Response text:', resp.text)
    raise

# If there's a download URL, fetch the file
download_url = None
if isinstance(res_json, dict):
    download_info = res_json.get('download') or res_json.get('file') or {}
    if isinstance(download_info, dict):
        download_url = download_info.get('url')
    elif isinstance(download_info, str):
        download_url = download_info

if download_url:
    if download_url.startswith('/'):
        download_url = DOWNLOAD_BASE + download_url
    print('Downloading generated file from', download_url)
    r = requests.get(download_url)
    if r.status_code == 200:
        out_path = os.path.join('..', 'samples', 'output_generated_ml.xlsx')
        with open(out_path, 'wb') as f:
            f.write(r.content)
        print('Saved generated file to', os.path.abspath(out_path))
    else:
        print('Failed to download file, status', r.status_code)
else:
    print('No download URL returned by the API')
