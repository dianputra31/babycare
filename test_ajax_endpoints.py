import requests
import json

# Test endpoint jenis terapi price
try:
    response = requests.get('http://127.0.0.1:8000/ajax/jenis-terapi/1/price/')
    print('=== Test Jenis Terapi Price Endpoint ===')
    print(f'Status Code: {response.status_code}')
    print(f'Content-Type: {response.headers.get("Content-Type")}')
    print(f'Raw Response (first 500 chars):\n{response.text[:500]}')
    if response.headers.get('Content-Type', '').startswith('application/json'):
        data = response.json()
        print(f'JSON Response: {json.dumps(data, indent=2)}')
except Exception as e:
    print(f'Error: {e}')

print('\n' + '='*60 + '\n')

# Test endpoint terapis transport
try:
    response = requests.get('http://127.0.0.1:8000/ajax/terapis/1/transport/')
    print('=== Test Terapis Transport Endpoint ===')
    print(f'Status Code: {response.status_code}')
    print(f'Content-Type: {response.headers.get("Content-Type")}')
    print(f'Raw Response (first 500 chars):\n{response.text[:500]}')
    if response.headers.get('Content-Type', '').startswith('application/json'):
        data = response.json()
        print(f'JSON Response: {json.dumps(data, indent=2)}')
except Exception as e:
    print(f'Error: {e}')
