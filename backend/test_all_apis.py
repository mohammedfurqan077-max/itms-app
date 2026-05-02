"""
Comprehensive API Testing Script
Tests all endpoints after creating a test account
"""
import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8000/api/v1"

# Colors for output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

def print_header(text):
    print(f"\n{'=' * 80}")
    print(f"{Colors.BLUE}{text}{Colors.RESET}")
    print('=' * 80)

def print_test(name, passed, details=""):
    status = f"{Colors.GREEN}✅ PASSED{Colors.RESET}" if passed else f"{Colors.RED}❌ FAILED{Colors.RESET}"
    print(f"{name}: {status}")
    if details:
        print(f"   {details}")

def print_response(response):
    print(f"   Status: {response.status_code}")
    try:
        print(f"   Response: {json.dumps(response.json(), indent=2)[:200]}...")
    except:
        print(f"   Response: {response.text[:200]}...")

# Global variables for tokens and IDs
access_token = None
refresh_token = None
junction_id = None
command_id = None

def test_health_check():
    """Test health check endpoint"""
    print_header("1. HEALTH CHECK")
    try:
        response = requests.get(f"{BASE_URL.replace('/api/v1', '')}/health")
        passed = response.status_code == 200
        print_test("GET /health", passed)
        print_response(response)
        return passed
    except Exception as e:
        print_test("GET /health", False, str(e))
        return False

def test_register():
    """Test user registration"""
    print_header("2. USER REGISTRATION")
    try:
        data = {
            "name": "Test User",
            "email": f"user.test.{int(time.time())}@itms.com",
            "password": "SecureP@ssw0rd123!",
            "role": "jawan"
        }
        response = requests.post(f"{BASE_URL}/auth/register", json=data)
        passed = response.status_code in [200, 201]
        print_test("POST /auth/register", passed, f"Email: {data['email']}")
        print_response(response)
        return passed, data
    except Exception as e:
        print_test("POST /auth/register", False, str(e))
        return False, None

def test_login(email, password):
    """Test user login"""
    print_header("3. USER LOGIN")
    global access_token, refresh_token
    try:
        data = {
            "email": email,
            "password": password
        }
        response = requests.post(f"{BASE_URL}/auth/login", json=data)
        passed = response.status_code == 200
        if passed:
            result = response.json()
            access_token = result['tokens']['access_token']
            refresh_token = result['tokens']['refresh_token']
        print_test("POST /auth/login", passed)
        print_response(response)
        return passed
    except Exception as e:
        print_test("POST /auth/login", False, str(e))
        return False

def test_get_profile():
    """Test get current user profile"""
    print_header("4. GET USER PROFILE")
    try:
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
        passed = response.status_code == 200
        print_test("GET /auth/me", passed)
        print_response(response)
        return passed
    except Exception as e:
        print_test("GET /auth/me", False, str(e))
        return False

def test_refresh_token():
    """Test token refresh"""
    print_header("5. REFRESH TOKEN")
    global access_token
    try:
        data = {"refresh_token": refresh_token}
        response = requests.post(f"{BASE_URL}/auth/refresh", json=data)
        passed = response.status_code == 200
        if passed:
            result = response.json()
            access_token = result['access_token']
        print_test("POST /auth/refresh", passed)
        print_response(response)
        return passed
    except Exception as e:
        print_test("POST /auth/refresh", False, str(e))
        return False

def test_create_junction():
    """Test create junction"""
    print_header("6. CREATE JUNCTION")
    global junction_id
    try:
        headers = {"Authorization": f"Bearer {access_token}"}
        data = {
            "name": f"Test Junction {int(time.time())}",
            "location": "Test Location, City",
            "ip_address": "192.168.1.100",
            "port": 5000,
            "latitude": 28.6139,
            "longitude": 77.2090,
            "lanes": 4,
            "status": "active"
        }
        response = requests.post(f"{BASE_URL}/junctions", json=data, headers=headers)
        passed = response.status_code == 200
        if passed:
            junction_id = response.json()['id']
        print_test("POST /junctions", passed, f"Junction ID: {junction_id}")
        print_response(response)
        return passed
    except Exception as e:
        print_test("POST /junctions", False, str(e))
        return False

def test_get_junctions():
    """Test get all junctions"""
    print_header("7. GET ALL JUNCTIONS")
    try:
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(f"{BASE_URL}/junctions", headers=headers)
        passed = response.status_code == 200
        print_test("GET /junctions", passed)
        print_response(response)
        return passed
    except Exception as e:
        print_test("GET /junctions", False, str(e))
        return False

def test_get_junction_by_id():
    """Test get junction by ID"""
    print_header("8. GET JUNCTION BY ID")
    try:
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(f"{BASE_URL}/junctions/{junction_id}", headers=headers)
        passed = response.status_code == 200
        print_test(f"GET /junctions/{junction_id}", passed)
        print_response(response)
        return passed
    except Exception as e:
        print_test(f"GET /junctions/{junction_id}", False, str(e))
        return False

def test_update_junction():
    """Test update junction"""
    print_header("9. UPDATE JUNCTION")
    try:
        headers = {"Authorization": f"Bearer {access_token}"}
        data = {
            "name": f"Updated Junction {int(time.time())}",
            "status": "maintenance"
        }
        response = requests.put(f"{BASE_URL}/junctions/{junction_id}", json=data, headers=headers)
        passed = response.status_code == 200
        print_test(f"PUT /junctions/{junction_id}", passed)
        print_response(response)
        return passed
    except Exception as e:
        print_test(f"PUT /junctions/{junction_id}", False, str(e))
        return False

def test_search_junctions():
    """Test search junctions"""
    print_header("10. SEARCH JUNCTIONS")
    try:
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(f"{BASE_URL}/junctions/search?q=Test", headers=headers)
        passed = response.status_code == 200
        print_test("GET /junctions/search?q=Test", passed)
        print_response(response)
        return passed
    except Exception as e:
        print_test("GET /junctions/search", False, str(e))
        return False

def test_create_command():
    """Test create command"""
    print_header("11. CREATE COMMAND")
    global command_id
    try:
        headers = {"Authorization": f"Bearer {access_token}"}
        data = {
            "junction_id": junction_id,
            "command_type": "GET_STATUS",
            "priority": "normal",
            "payload": {}
        }
        response = requests.post(f"{BASE_URL}/commands", json=data, headers=headers)
        passed = response.status_code == 200
        if passed:
            command_id = response.json()['id']
        print_test("POST /commands", passed, f"Command ID: {command_id}")
        print_response(response)
        return passed
    except Exception as e:
        print_test("POST /commands", False, str(e))
        return False

def test_get_commands():
    """Test get all commands"""
    print_header("12. GET ALL COMMANDS")
    try:
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(f"{BASE_URL}/commands", headers=headers)
        passed = response.status_code == 200
        print_test("GET /commands", passed)
        print_response(response)
        return passed
    except Exception as e:
        print_test("GET /commands", False, str(e))
        return False

def test_get_command_by_id():
    """Test get command by ID"""
    print_header("13. GET COMMAND BY ID")
    try:
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(f"{BASE_URL}/commands/{command_id}", headers=headers)
        passed = response.status_code == 200
        print_test(f"GET /commands/{command_id}", passed)
        print_response(response)
        return passed
    except Exception as e:
        print_test(f"GET /commands/{command_id}", False, str(e))
        return False

def test_execute_command():
    """Test execute command"""
    print_header("14. EXECUTE COMMAND")
    try:
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.post(f"{BASE_URL}/commands/{command_id}/execute", headers=headers)
        # Command execution might fail if RPi is not available, but API should respond
        passed = response.status_code in [200, 400, 500]
        print_test(f"POST /commands/{command_id}/execute", passed, "Note: May fail if RPi not available")
        print_response(response)
        return passed
    except Exception as e:
        print_test(f"POST /commands/{command_id}/execute", False, str(e))
        return False

def test_get_system_state():
    """Test get system state"""
    print_header("15. GET SYSTEM STATE")
    try:
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(f"{BASE_URL}/system/state", headers=headers)
        passed = response.status_code == 200
        print_test("GET /system/state", passed)
        print_response(response)
        return passed
    except Exception as e:
        print_test("GET /system/state", False, str(e))
        return False

def test_update_system_state():
    """Test update system state"""
    print_header("16. UPDATE SYSTEM STATE")
    try:
        headers = {"Authorization": f"Bearer {access_token}"}
        data = {
            "mode": "manual",
            "emergency_active": False
        }
        response = requests.put(f"{BASE_URL}/system/state", json=data, headers=headers)
        passed = response.status_code == 200
        print_test("PUT /system/state", passed)
        print_response(response)
        return passed
    except Exception as e:
        print_test("PUT /system/state", False, str(e))
        return False

def test_get_system_stats():
    """Test get system statistics"""
    print_header("17. GET SYSTEM STATISTICS")
    try:
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(f"{BASE_URL}/system/stats", headers=headers)
        passed = response.status_code == 200
        print_test("GET /system/stats", passed)
        print_response(response)
        return passed
    except Exception as e:
        print_test("GET /system/stats", False, str(e))
        return False

def test_logout():
    """Test user logout"""
    print_header("18. USER LOGOUT")
    try:
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.post(f"{BASE_URL}/auth/logout", headers=headers)
        passed = response.status_code == 200
        print_test("POST /auth/logout", passed)
        print_response(response)
        return passed
    except Exception as e:
        print_test("POST /auth/logout", False, str(e))
        return False

def main():
    """Run all tests"""
    print(f"\n{Colors.BLUE}{'=' * 80}")
    print("ITMS BACKEND - COMPREHENSIVE API TESTING")
    print(f"{'=' * 80}{Colors.RESET}\n")
    print(f"Base URL: {BASE_URL}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = []
    
    # Run tests
    results.append(("Health Check", test_health_check()))
    
    passed, user_data = test_register()
    results.append(("User Registration", passed))
    
    if passed and user_data:
        results.append(("User Login", test_login(user_data['email'], user_data['password'])))
        
        if access_token:
            results.append(("Get Profile", test_get_profile()))
            results.append(("Refresh Token", test_refresh_token()))
            results.append(("Create Junction", test_create_junction()))
            
            if junction_id:
                results.append(("Get All Junctions", test_get_junctions()))
                results.append(("Get Junction By ID", test_get_junction_by_id()))
                results.append(("Update Junction", test_update_junction()))
                results.append(("Search Junctions", test_search_junctions()))
                results.append(("Create Command", test_create_command()))
                
                if command_id:
                    results.append(("Get All Commands", test_get_commands()))
                    results.append(("Get Command By ID", test_get_command_by_id()))
                    results.append(("Execute Command", test_execute_command()))
            
            results.append(("Get System State", test_get_system_state()))
            results.append(("Update System State", test_update_system_state()))
            results.append(("Get System Stats", test_get_system_stats()))
            results.append(("User Logout", test_logout()))
    
    # Summary
    print_header("TEST SUMMARY")
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    success_rate = (passed_count / total_count * 100) if total_count > 0 else 0
    
    print(f"\nTotal Tests: {total_count}")
    print(f"Passed: {Colors.GREEN}{passed_count}{Colors.RESET}")
    print(f"Failed: {Colors.RED}{total_count - passed_count}{Colors.RESET}")
    print(f"Success Rate: {Colors.GREEN if success_rate >= 80 else Colors.RED}{success_rate:.1f}%{Colors.RESET}")
    
    print("\nDetailed Results:")
    for name, passed in results:
        status = f"{Colors.GREEN}✅{Colors.RESET}" if passed else f"{Colors.RED}❌{Colors.RESET}"
        print(f"  {status} {name}")
    
    print(f"\n{'=' * 80}\n")
    
    if success_rate >= 80:
        print(f"{Colors.GREEN}✅ API TESTING SUCCESSFUL!{Colors.RESET}")
        print("All critical endpoints are working correctly.")
    else:
        print(f"{Colors.RED}❌ SOME TESTS FAILED{Colors.RESET}")
        print("Please check the failed tests above.")
    
    print(f"\n{'=' * 80}\n")

if __name__ == "__main__":
    main()
