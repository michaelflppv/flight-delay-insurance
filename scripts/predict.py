#!/usr/bin/env python3
"""
Test client for making prediction requests
"""

import sys
import os
from pathlib import Path
import requests
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Get API endpoint from environment
# Use 127.0.0.1 to match Flask server binding
API_HOST = os.getenv('API_HOST', '127.0.0.1')
API_PORT = os.getenv('API_PORT', os.getenv('FLASK_PORT', '5000'))
url = f'http://{API_HOST}:{API_PORT}/predict'

print(f"Sending request to: {url}")

# Example request data
data = {
    'POLICY_ID': 1,
    'AIRLINE_CODE': 'NK',
    'ORIGIN': 'DEN',        # Denver International Airport
    'DEST': 'IAH',          # Houston George Bush Intercontinental
    'DISTANCE': 863,         # Distance in miles
    'CRS_DEP_TIME': 1534,
    'FL_DATE': '2024-07-15'
}

try:
    response = requests.post(url, json=data, timeout=10)

    if response.status_code == 200:
        result = response.json()
        print(f"\\nSuccess!")
        print(f"Insurance price: ${result['insurance_price']}")
        print(f"Delay probability: {result.get('delay_probability', 'N/A')}")
        print(f"Is delayed: {result.get('is_delayed', 'N/A')}")
        print(f"Predicted delay: {result.get('predicted_delay_minutes', 0)} minutes")
        sys.exit(0)
    else:
        print(f"\\nRequest failed with status code {response.status_code}")
        print(f"Error: {response.json()}")
        sys.exit(1)

except requests.exceptions.ConnectionError:
    print(f"\\nError: Could not connect to {url}")
    print("Please ensure the server is running with: make run")
    sys.exit(1)
except requests.exceptions.Timeout:
    print(f"\\nError: Request timed out")
    sys.exit(1)
except Exception as e:
    print(f"\\nUnexpected error: {e}")
    sys.exit(1)
