import requests
import json

API = 'http://localhost:8009/api/files/preview-ml-file'
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

print('Sending preview request to', API)
resp = requests.post(API, files=files, data=data)

try:
    print('Status code:', resp.status_code)
    print(json.dumps(resp.json(), indent=2, ensure_ascii=False))
except Exception as e:
    print('Response text:', resp.text)
    print('Error parsing JSON:', e)
