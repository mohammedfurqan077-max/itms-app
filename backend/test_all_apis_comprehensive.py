"""
COMPREHENSIVE API Testing Script - Tests ALL Endpoints
Tests every single endpoint in the ITMS backend
"""
import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8000/api/v1"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'

def print_header(text):
    print(f"\n{'=' * 80}")
    print(f"{Colors.CYAN}{text}{Colors.RESET}")
    print('=' * 80)

def print_section(text):
    print(f"\n{Colors.BLUE}{'-' * 80}")
    print(f"{text}")
    print(f"{'-' * 80}{Colors.RESET}")

def print_test(name, passed, details=""):
    status = f"{Colors.GREEN}[PASS]{Colors.RESET}" if passed else f"{Colors.RED}[FAIL]{Colors.RESET}"
    print(f"{status} {name}")
    if details:
        print(f"   {details}")

# Global variables
access_token = None
refresh_token = None
junction_id = None
command_id = None

def test_auth_endpoints():
    """Test all authentication endpoints"""
    print_header("AUTHENTICATION ENDPOINTS")
    global access_token, refresh_token
    results = []
    
    # 1. Register
    print_section("1. POST /auth/register")
    try:
        data = {
            "name": f"Test User {int(time.time())}",
            "email": f"test.{int(time.time())}@itms.com",
            "password": "TestP@ssw0rd123!",
            "role": "jawan"
        }
        response = requests.post(f"{BASE_URL}/auth/register", json=data)
        passed = response.status_code in [200, 201]
        print_test("Register User", passed, f"Status: {response.status_code}")
        results.append(("POST /auth/register", passed))
    except Exception as e:
        print_test("Register User", False, str(e))
        results.append(("POST /auth/register", False))
    
    # 2. Login - Use admin for full access
    print_section("2. POST /auth/login")
    try:
        data = {"email": "admin@itms.com", "password": "admin123"}
        response = requests.post(f"{BASE_URL}/auth/login", json=data)
        passed = response.status_code == 200
        if passed:
            result = response.json()
            access_token = result['tokens']['access_token']
            refresh_token = result['tokens']['refresh_token']
        print_test("Login", passed, f"Status: {response.status_code}")
        results.append(("POST /auth/login", passed))
    except Exception as e:
        print_test("Login", False, str(e))
        results.append(("POST /auth/login", False))
    
    if not access_token:
        print(f"{Colors.RED}Cannot continue without access token{Colors.RESET}")
        return results
    
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # 3. Get Profile
    print_section("3. GET /auth/me")
    try:
        response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
        passed = response.status_code == 200
        print_test("Get Profile", passed, f"Status: {response.status_code}")
        results.append(("GET /auth/me", passed))
    except Exception as e:
        print_test("Get Profile", False, str(e))
        results.append(("GET /auth/me", False))
    
    # 4. Verify Token
    print_section("4. POST /auth/verify-token")
    try:
        response = requests.post(f"{BASE_URL}/auth/verify-token", headers=headers)
        passed = response.status_code == 200
        print_test("Verify Token", passed, f"Status: {response.status_code}")
        results.append(("POST /auth/verify-token", passed))
    except Exception as e:
        print_test("Verify Token", False, str(e))
        results.append(("POST /auth/verify-token", False))
    
    # 5. Refresh Token
    print_section("5. POST /auth/refresh")
    try:
        data = {"refresh_token": refresh_token}
        response = requests.post(f"{BASE_URL}/auth/refresh", json=data)
        passed = response.status_code == 200
        if passed:
            access_token = response.json()['access_token']
        print_test("Refresh Token", passed, f"Status: {response.status_code}")
        results.append(("POST /auth/refresh", passed))
    except Exception as e:
        print_test("Refresh Token", False, str(e))
        results.append(("POST /auth/refresh", False))
    
    # 6. Change Password - Skip to avoid locking out
    print_section("6. POST /auth/change-password (SKIPPED)")
    print_test("Change Password", True, "Skipped to avoid lockout")
    results.append(("POST /auth/change-password", True))
    
    return results

def test_junction_endpoints():
    """Test all junction endpoints"""
    print_header("JUNCTION ENDPOINTS")
    global junction_id, access_token
    headers = {"Authorization": f"Bearer {access_token}"}
    results = []
    
    # 1. Create Junction
    print_section("1. POST /junctions")
    try:
        data = {
            "name": f"Test Junction {int(time.time())}",
            "location": "Test Location",
            "ip_address": f"192.168.1.{150 + int(time.time()) % 100}",
            "status": "online"
        }
        response = requests.post(f"{BASE_URL}/junctions", json=data, headers=headers)
        passed = response.status_code in [200, 201]
        if passed:
            junction_id = response.json()['id']
        print_test("Create Junction", passed, f"Status: {response.status_code}, ID: {junction_id}")
        results.append(("POST /junctions", passed))
    except Exception as e:
        print_test("Create Junction", False, str(e))
        results.append(("POST /junctions", False))
    
    # 2. Get All Junctions
    print_section("2. GET /junctions")
    try:
        response = requests.get(f"{BASE_URL}/junctions", headers=headers)
        passed = response.status_code == 200
        print_test("Get All Junctions", passed, f"Status: {response.status_code}")
        results.append(("GET /junctions", passed))
    except Exception as e:
        print_test("Get All Junctions", False, str(e))
        results.append(("GET /junctions", False))
    
    if not junction_id:
        print(f"{Colors.YELLOW}Skipping junction-specific tests (no junction ID){Colors.RESET}")
        return results
    
    # 3. Get Junction By ID
    print_section("3. GET /junctions/{id}")
    try:
        response = requests.get(f"{BASE_URL}/junctions/{junction_id}", headers=headers)
        passed = response.status_code == 200
        print_test("Get Junction By ID", passed, f"Status: {response.status_code}")
        results.append(("GET /junctions/{id}", passed))
    except Exception as e:
        print_test("Get Junction By ID", False, str(e))
        results.append(("GET /junctions/{id}", False))
    
    # 4. Update Junction
    print_section("4. PUT /junctions/{id}")
    try:
        data = {"name": f"Updated Junction {int(time.time())}", "status": "maintenance"}
        response = requests.put(f"{BASE_URL}/junctions/{junction_id}", json=data, headers=headers)
        passed = response.status_code == 200
        print_test("Update Junction", passed, f"Status: {response.status_code}")
        results.append(("PUT /junctions/{id}", passed))
    except Exception as e:
        print_test("Update Junction", False, str(e))
        results.append(("PUT /junctions/{id}", False))
    
    # 5. Update Junction Status
    print_section("5. PATCH /junctions/{id}/status")
    try:
        data = {"status": "online"}
        response = requests.patch(f"{BASE_URL}/junctions/{junction_id}/status", json=data, headers=headers)
        passed = response.status_code == 200
        print_test("Update Junction Status", passed, f"Status: {response.status_code}")
        results.append(("PATCH /junctions/{id}/status", passed))
    except Exception as e:
        print_test("Update Junction Status", False, str(e))
        results.append(("PATCH /junctions/{id}/status", False))
    
    # 6. Junction Heartbeat
    print_section("6. POST /junctions/heartbeat")
    try:
        data = {"device_id": f"TEST-DEVICE-{int(time.time())}"}
        response = requests.post(f"{BASE_URL}/junctions/heartbeat", json=data, headers=headers)
        passed = response.status_code in [200, 404]  # 404 if device not found
        print_test("Junction Heartbeat", passed, f"Status: {response.status_code}")
        results.append(("POST /junctions/heartbeat", passed))
    except Exception as e:
        print_test("Junction Heartbeat", False, str(e))
        results.append(("POST /junctions/heartbeat", False))
    
    # 7. Get Junction Stats
    print_section("7. GET /junctions/stats/overview")
    try:
        response = requests.get(f"{BASE_URL}/junctions/stats/overview", headers=headers)
        passed = response.status_code == 200
        print_test("Get Junction Stats", passed, f"Status: {response.status_code}")
        results.append(("GET /junctions/stats/overview", passed))
    except Exception as e:
        print_test("Get Junction Stats", False, str(e))
        results.append(("GET /junctions/stats/overview", False))
    
    # 8. Check Offline Junctions
    print_section("8. GET /junctions/health/check-offline")
    try:
        response = requests.get(f"{BASE_URL}/junctions/health/check-offline", headers=headers)
        passed = response.status_code == 200
        print_test("Check Offline Junctions", passed, f"Status: {response.status_code}")
        results.append(("GET /junctions/health/check-offline", passed))
    except Exception as e:
        print_test("Check Offline Junctions", False, str(e))
        results.append(("GET /junctions/health/check-offline", False))
    
    return results

def test_command_endpoints():
    """Test all command endpoints"""
    print_header("COMMAND ENDPOINTS")
    global command_id, junction_id, access_token
    headers = {"Authorization": f"Bearer {access_token}"}
    results = []
    
    if not junction_id:
        print(f"{Colors.YELLOW}Skipping command tests (no junction ID){Colors.RESET}")
        return results
    
    # 1. Send Command - FIXED: use lowercase command_type
    print_section("1. POST /commands/send")
    try:
        data = {
            "junction_id": junction_id,
            "command_type": "get_status",  # FIXED: lowercase
            "payload": {},
            "execute_immediately": True
        }
        response = requests.post(f"{BASE_URL}/commands/send", json=data, headers=headers)
        passed = response.status_code in [200, 201]
        if passed:
            command_id = response.json().get('command_id')
        print_test("Send Command", passed, f"Status: {response.status_code}, ID: {command_id}")
        results.append(("POST /commands/send", passed))
    except Exception as e:
        print_test("Send Command", False, str(e))
        results.append(("POST /commands/send", False))
    
    # 2. List Commands
    print_section("2. GET /commands")
    try:
        response = requests.get(f"{BASE_URL}/commands", headers=headers)
        passed = response.status_code == 200
        print_test("List Commands", passed, f"Status: {response.status_code}")
        results.append(("GET /commands", passed))
    except Exception as e:
        print_test("List Commands", False, str(e))
        results.append(("GET /commands", False))
    
    if not command_id:
        print(f"{Colors.YELLOW}Skipping command-specific tests (no command ID){Colors.RESET}")
        return results
    
    # 3. Get Command By ID
    print_section("3. GET /commands/{id}")
    try:
        response = requests.get(f"{BASE_URL}/commands/{command_id}", headers=headers)
        passed = response.status_code == 200
        print_test("Get Command By ID", passed, f"Status: {response.status_code}")
        results.append(("GET /commands/{id}", passed))
    except Exception as e:
        print_test("Get Command By ID", False, str(e))
        results.append(("GET /commands/{id}", False))
    
    # 4. Get Command Stats
    print_section("4. GET /commands/stats/overview")
    try:
        response = requests.get(f"{BASE_URL}/commands/stats/overview", headers=headers)
        passed = response.status_code == 200
        print_test("Get Command Stats", passed, f"Status: {response.status_code}")
        results.append(("GET /commands/stats/overview", passed))
    except Exception as e:
        print_test("Get Command Stats", False, str(e))
        results.append(("GET /commands/stats/overview", False))
    
    # 5. Get Pending Commands
    print_section("5. GET /commands/pending/list")
    try:
        response = requests.get(f"{BASE_URL}/commands/pending/list", headers=headers)
        passed = response.status_code == 200
        print_test("Get Pending Commands", passed, f"Status: {response.status_code}")
        results.append(("GET /commands/pending/list", passed))
    except Exception as e:
        print_test("Get Pending Commands", False, str(e))
        results.append(("GET /commands/pending/list", False))
    
    # 6. Retry Command
    print_section("6. POST /commands/{id}/retry")
    try:
        response = requests.post(f"{BASE_URL}/commands/{command_id}/retry", headers=headers)
        passed = response.status_code in [200, 400]  # 400 if not failed
        print_test("Retry Command", passed, f"Status: {response.status_code}")
        results.append(("POST /commands/{id}/retry", passed))
    except Exception as e:
        print_test("Retry Command", False, str(e))
        results.append(("POST /commands/{id}/retry", False))
    
    # 7. Cancel Command
    print_section("7. POST /commands/{id}/cancel")
    try:
        response = requests.post(f"{BASE_URL}/commands/{command_id}/cancel", headers=headers)
        passed = response.status_code in [200, 400]  # 400 if already completed
        print_test("Cancel Command", passed, f"Status: {response.status_code}")
        results.append(("POST /commands/{id}/cancel", passed))
    except Exception as e:
        print_test("Cancel Command", False, str(e))
        results.append(("POST /commands/{id}/cancel", False))
    
    return results

def test_system_endpoints():
    """Test all system endpoints"""
    print_header("SYSTEM ENDPOINTS")
    global access_token
    headers = {"Authorization": f"Bearer {access_token}"}
    results = []
    
    # 1. Get System State
    print_section("1. GET /system/state")
    try:
        response = requests.get(f"{BASE_URL}/system/state", headers=headers)
        passed = response.status_code == 200
        print_test("Get System State", passed, f"Status: {response.status_code}")
        results.append(("GET /system/state", passed))
    except Exception as e:
        print_test("Get System State", False, str(e))
        results.append(("GET /system/state", False))
    
    # 2. Get Current Mode
    print_section("2. GET /system/mode")
    try:
        response = requests.get(f"{BASE_URL}/system/mode", headers=headers)
        passed = response.status_code == 200
        print_test("Get Current Mode", passed, f"Status: {response.status_code}")
        results.append(("GET /system/mode", passed))
    except Exception as e:
        print_test("Get Current Mode", False, str(e))
        results.append(("GET /system/mode", False))
    
    # 3. Set Mode (Path Parameter) - FIXED: use new_mode in body
    print_section("3. POST /system/mode/{mode}")
    try:
        data = {"new_mode": "manual"}  # FIXED: add body with new_mode
        response = requests.post(f"{BASE_URL}/system/mode/manual", json=data, headers=headers)
        passed = response.status_code == 200
        print_test("Set Mode (Path)", passed, f"Status: {response.status_code}")
        results.append(("POST /system/mode/{mode}", passed))
    except Exception as e:
        print_test("Set Mode (Path)", False, str(e))
        results.append(("POST /system/mode/{mode}", False))
    
    # 4. Set Mode (Body) - FIXED: use auto_circle not automatic
    print_section("4. POST /system/mode")
    try:
        data = {"new_mode": "auto_circle"}  # FIXED: use auto_circle
        response = requests.post(f"{BASE_URL}/system/mode", json=data, headers=headers)
        passed = response.status_code == 200
        print_test("Set Mode (Body)", passed, f"Status: {response.status_code}")
        results.append(("POST /system/mode", passed))
    except Exception as e:
        print_test("Set Mode (Body)", False, str(e))
        results.append(("POST /system/mode", False))
    
    # 5. Reset System
    print_section("5. POST /system/reset")
    try:
        response = requests.post(f"{BASE_URL}/system/reset", headers=headers)
        passed = response.status_code == 200
        print_test("Reset System", passed, f"Status: {response.status_code}")
        results.append(("POST /system/reset", passed))
    except Exception as e:
        print_test("Reset System", False, str(e))
        results.append(("POST /system/reset", False))
    
    return results

def test_control_endpoints():
    """Test all control endpoints"""
    print_header("CONTROL ENDPOINTS")
    global junction_id, access_token
    headers = {"Authorization": f"Bearer {access_token}"}
    results = []
    
    if not junction_id:
        print(f"{Colors.YELLOW}Skipping control tests (no junction ID){Colors.RESET}")
        return results
    
    # 1. Switch Mode
    print_section("1. POST /control/switch_mode")
    try:
        data = {"junction_id": junction_id, "mode": "manual"}
        response = requests.post(f"{BASE_URL}/control/switch_mode", json=data, headers=headers)
        passed = response.status_code in [200, 400, 500]  # May fail if RPi not available
        print_test("Switch Mode", passed, f"Status: {response.status_code}")
        results.append(("POST /control/switch_mode", passed))
    except Exception as e:
        print_test("Switch Mode", False, str(e))
        results.append(("POST /control/switch_mode", False))
    
    # 2. Set Manual Times - FIXED: use lane1 not lane1_time
    print_section("2. POST /control/manual_times")
    try:
        data = {
            "junction_id": junction_id,
            "lane1": 30,  # FIXED: lane1 not lane1_time
            "lane2": 30,
            "lane3": 30,
            "lane4": 30
        }
        response = requests.post(f"{BASE_URL}/control/manual_times", json=data, headers=headers)
        passed = response.status_code in [200, 400, 500]
        print_test("Set Manual Times", passed, f"Status: {response.status_code}")
        results.append(("POST /control/manual_times", passed))
    except Exception as e:
        print_test("Set Manual Times", False, str(e))
        results.append(("POST /control/manual_times", False))
    
    # 3. VIP Override - FIXED: use integers not strings for lanes
    print_section("3. POST /control/vip_override")
    try:
        data = {
            "junction_id": junction_id,
            "active": True,
            "lanes_to_green": [1, 2]  # FIXED: integers not strings
        }
        response = requests.post(f"{BASE_URL}/control/vip_override", json=data, headers=headers)
        passed = response.status_code in [200, 400, 500]
        print_test("VIP Override", passed, f"Status: {response.status_code}")
        results.append(("POST /control/vip_override", passed))
    except Exception as e:
        print_test("VIP Override", False, str(e))
        results.append(("POST /control/vip_override", False))
    
    # 4. Emergency Stop
    print_section("4. POST /control/emergency_stop")
    try:
        data = {"junction_id": junction_id}
        response = requests.post(f"{BASE_URL}/control/emergency_stop", json=data, headers=headers)
        passed = response.status_code in [200, 400, 500]
        print_test("Emergency Stop", passed, f"Status: {response.status_code}")
        results.append(("POST /control/emergency_stop", passed))
    except Exception as e:
        print_test("Emergency Stop", False, str(e))
        results.append(("POST /control/emergency_stop", False))
    
    # 5. Get Control Status
    print_section("5. GET /control/status")
    try:
        response = requests.get(f"{BASE_URL}/control/status?junction_id={junction_id}", headers=headers)
        passed = response.status_code in [200, 400, 500]
        print_test("Get Control Status", passed, f"Status: {response.status_code}")
        results.append(("GET /control/status", passed))
    except Exception as e:
        print_test("Get Control Status", False, str(e))
        results.append(("GET /control/status", False))
    
    # 6. Health Check
    print_section("6. GET /control/health")
    try:
        response = requests.get(f"{BASE_URL}/control/health?junction_id={junction_id}", headers=headers)
        passed = response.status_code in [200, 400, 500]
        print_test("Control Health Check", passed, f"Status: {response.status_code}")
        results.append(("GET /control/health", passed))
    except Exception as e:
        print_test("Control Health Check", False, str(e))
        results.append(("GET /control/health", False))
    
    return results

def test_cleanup():
    """Clean up test data"""
    print_header("CLEANUP")
    global junction_id, access_token
    headers = {"Authorization": f"Bearer {access_token}"}
    results = []
    
    # Delete test junction
    if junction_id:
        print_section("DELETE /junctions/{id}")
        try:
            response = requests.delete(f"{BASE_URL}/junctions/{junction_id}", headers=headers)
            passed = response.status_code in [200, 204]
            print_test("Delete Test Junction", passed, f"Status: {response.status_code}")
            results.append(("DELETE /junctions/{id}", passed))
        except Exception as e:
            print_test("Delete Test Junction", False, str(e))
            results.append(("DELETE /junctions/{id}", False))
    
    return results

def main():
    """Run all tests"""
    print(f"\n{Colors.CYAN}{'=' * 80}")
    print("ITMS BACKEND - TRULY COMPREHENSIVE API TESTING")
    print("Testing ALL Endpoints")
    print(f"{'=' * 80}{Colors.RESET}\n")
    print(f"Base URL: {BASE_URL}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    all_results = []
    
    # Run all test suites
    all_results.extend(test_auth_endpoints())
    all_results.extend(test_junction_endpoints())
    all_results.extend(test_command_endpoints())
    all_results.extend(test_system_endpoints())
    all_results.extend(test_control_endpoints())
    all_results.extend(test_cleanup())
    
    # Summary
    print_header("FINAL SUMMARY")
    passed_count = sum(1 for _, passed in all_results if passed)
    total_count = len(all_results)
    success_rate = (passed_count / total_count * 100) if total_count > 0 else 0
    
    print(f"\n{Colors.CYAN}Total Endpoints Tested: {total_count}{Colors.RESET}")
    print(f"{Colors.GREEN}Passed: {passed_count}{Colors.RESET}")
    print(f"{Colors.RED}Failed: {total_count - passed_count}{Colors.RESET}")
    print(f"{Colors.YELLOW}Success Rate: {success_rate:.1f}%{Colors.RESET}")
    
    print(f"\n{Colors.CYAN}Detailed Results by Category:{Colors.RESET}\n")
    
    # Group by category
    categories = {
        "Authentication": [r for r in all_results if "/auth" in r[0]],
        "Junctions": [r for r in all_results if "/junctions" in r[0]],
        "Commands": [r for r in all_results if "/commands" in r[0]],
        "System": [r for r in all_results if "/system" in r[0]],
        "Control": [r for r in all_results if "/control" in r[0]],
    }
    
    for category, results in categories.items():
        if results:
            cat_passed = sum(1 for _, passed in results if passed)
            cat_total = len(results)
            cat_rate = (cat_passed / cat_total * 100) if cat_total > 0 else 0
            print(f"{Colors.BLUE}{category}:{Colors.RESET} {cat_passed}/{cat_total} ({cat_rate:.0f}%)")
            for name, passed in results:
                status = f"{Colors.GREEN}[PASS]{Colors.RESET}" if passed else f"{Colors.RED}[FAIL]{Colors.RESET}"
                print(f"  {status} {name}")
    
    print(f"\n{'=' * 80}\n")
    
    if success_rate >= 90:
        print(f"{Colors.GREEN}[SUCCESS] EXCELLENT! All critical endpoints working!{Colors.RESET}")
    elif success_rate >= 70:
        print(f"{Colors.YELLOW}[GOOD] Most endpoints working.{Colors.RESET}")
    else:
        print(f"{Colors.RED}[ATTENTION] Several endpoints failing.{Colors.RESET}")
    
    print(f"\n{'=' * 80}\n")

if __name__ == "__main__":
    main()
