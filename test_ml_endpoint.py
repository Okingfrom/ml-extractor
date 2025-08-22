import requests
import json

# Test the ML analysis endpoint
url = "http://localhost:8005/api/files/analyze-ml-template"

# Test with the sample file we created
file_path = "samples/plantilla_ml_ejemplo.csv"

try:
    with open(file_path, 'rb') as f:
        files = {'file': f}
        response = requests.post(url, files=files)
        
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
except Exception as e:
    print(f"Error: {e}")
