"""
Test junction creation to debug the status issue
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

# Login as admin
login_response = requests.post(
    f"{BASE_URL}/auth/login",
    json={"email": "admin@itms.com", "password": "admin123"}
)

if login_response.status_code != 200:
    print(f"Login failed: {login_response.status_code}")
    print(login_response.text)
    exit(1)

token = login_response.json()['tokens']['access_token']
print(f"✅ Logged in successfully")
print(f"Token: {token[:50]}...")

# Try creating junction with different status values
test_cases = [
    {"name": "Test Junction 1", "location": "Location 1", "ip_address": "192.168.1.101", "status": "online"},
    {"name": "Test Junction 2", "location": "Location 2", "ip_address": "192.168.1.102", "status": "ONLINE"},
    {"name": "Test Junction 3", "location": "Location 3", "ip_address": "192.168.1.103"},  # No status
]

headers = {"Authorization": f"Bearer {token}"}

for i, data in enumerate(test_cases, 1):
    print(f"\n{'='*80}")
    print(f"Test {i}: {data.get('name')}")
    print(f"Status: {data.get('status', 'NOT PROVIDED (will use default)')}")
    print('='*80)
    
    response = requests.post(f"{BASE_URL}/junctions", json=data, headers=headers)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response:")
    try:
        print(json.dumps(response.json(), indent=2))
    except:
        print(response.text)
    
    if response.status_code in [200, 201]:
        print("✅ SUCCESS")
    else:
        print("❌ FAILED")
