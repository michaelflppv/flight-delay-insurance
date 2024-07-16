import requests

url = 'http://192.168.0.100:5000/predict'

data = {
    'AIRLINE_CODE': 'NK',
    'ORIGIN_CITY': 'Denver, CO',
    'DEST_CITY': 'Houston, TX',
    'CRS_DEP_TIME': 1534,
    'FL_DATE': '2024-07-15'
}

response = requests.post(url, json=data)

if response.status_code == 200:
    result = response.json()
    print(f"Insurance price: {result['insurance_price']} dollars")
else:
    print(f"Request failed with status code {response.status_code}")