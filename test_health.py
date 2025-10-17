#!/usr/bin/env python
import requests
import json

try:
    response = requests.get('http://127.0.0.1:8000/health/', timeout=10)
    print("🔍 Health Check Response:")
    print("=" * 50)
    print(f"Status Code: {response.status_code}")
    print(f"Content-Type: {response.headers.get('content-type', 'Unknown')}")
    print()
    
    if response.status_code == 200:
        data = response.json()
        print("📊 Health Check Data:")
        print(json.dumps(data, indent=2))
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
        
except requests.exceptions.ConnectionError:
    print("❌ Connection Error: Server not running on http://127.0.0.1:8000")
except Exception as e:
    print(f"❌ Error: {e}")