"""
Debug script to see exact error messages for failing endpoints
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

# Login first - try jawan account
login_response = requests.post(
    f"{BASE_URL}/auth/login",
    json={"email": "jawan@itms.com", "password": "jawan123"}
)

if login_response.status_code != 200:
    print(f"Login failed: {login_response.status_code}")
    print(login_response.text)
    exit(1)

token = login_response.json()['tokens']['access_token']
headers = {"Authorization": f"Bearer {token}"}

print("=" * 80)
print("DEBUGGING FAILING ENDPOINTS")
print("=" * 80)

# 1. POST /commands/send
print("\n1. POST /commands/send")
print("-" * 80)
data = {
    "junction_id": 1,
    "command_type": "GET_STATUS",
    "priority": "normal",
    "payload": {}
}
response = requests.post(f"{BASE_URL}/commands/send", json=data, headers=headers)
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")

# 2. POST /system/mode/{mode}
print("\n2. POST /system/mode/manual")
print("-" * 80)
response = requests.post(f"{BASE_URL}/system/mode/manual", headers=headers)
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")

# 3. POST /system/mode
print("\n3. POST /system/mode")
print("-" * 80)
data = {"mode": "automatic"}
response = requests.post(f"{BASE_URL}/system/mode", json=data, headers=headers)
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")

# 4. POST /control/manual_times
print("\n4. POST /control/manual_times")
print("-" * 80)
data = {
    "junction_id": 1,
    "lane1_time": 30,
    "lane2_time": 30,
    "lane3_time": 30,
    "lane4_time": 30
}
response = requests.post(f"{BASE_URL}/control/manual_times", json=data, headers=headers)
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")

# 5. POST /control/vip_override
print("\n5. POST /control/vip_override")
print("-" * 80)
data = {
    "junction_id": 1,
    "active": True,
    "lanes_to_green": ["lane1", "lane2"]
}
response = requests.post(f"{BASE_URL}/control/vip_override", json=data, headers=headers)
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")

print("\n" + "=" * 80)
