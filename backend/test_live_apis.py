"""
Test Live API Endpoints
Tests all API endpoints on running server
"""
import asyncio
import httpx
import sys

# Your Dev Tunnel URL
API_BASE_URL = "https://qsdn8gwg-8000.inc1.devtunnels.ms/api/v1"
HEALTH_URL = "https://qsdn8gwg-8000.inc1.devtunnels.ms/health"


async def test_apis():
    """Test all API endpoints"""
    print("="*70)
    print("TESTING LIVE API ENDPOINTS")
    print("="*70)
    print(f"\nAPI URL: {API_BASE_URL}")
    print(f"Health URL: {HEALTH_URL}\n")
    
    passed = 0
    failed = 0
    token = None
    
    async with httpx.AsyncClient(timeout=30.0, verify=False) as client:
        # Test 1: Health Check
        print("1. Testing Health Endpoint...")
        try:
            response = await client.get(HEALTH_URL)
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ PASS: GET /health")
                print(f"      Status: {data.get('status')}")
                print(f"      App: {data.get('app')}")
                print(f"      Version: {data.get('version')}")
                passed += 1
            else:
                print(f"   ❌ FAIL: GET /health (Status: {response.status_code})")
                failed += 1
        except Exception as e:
            print(f"   ❌ FAIL: GET /health")
            print(f"      Error: {str(e)}")
            failed += 1
        
        # Test 2: Login
        print("\n2. Testing Login Endpoint...")
        try:
            response = await client.post(
                f"{API_BASE_URL}/auth/login",
                json={"email": "admin@itms.com", "password": "admin123"}
            )
            if response.status_code == 200:
                data = response.json()
                # Handle different response formats
                if "access_token" in data:
                    token = data["access_token"]
                elif "tokens" in data and "access_token" in data["tokens"]:
                    token = data["tokens"]["access_token"]
                elif "token" in data:
                    token = data["token"]
                
                if token:
                    print(f"   ✅ PASS: POST /auth/login")
                    print(f"      Token received: {token[:20]}...")
                    passed += 1
                else:
                    print(f"   ❌ FAIL: POST /auth/login (No token in response)")
                    print(f"      Response: {data}")
                    failed += 1
            else:
                print(f"   ❌ FAIL: POST /auth/login (Status: {response.status_code})")
                print(f"      Response: {response.text}")
                failed += 1
        except Exception as e:
            print(f"   ❌ FAIL: POST /auth/login")
            print(f"      Error: {str(e)}")
            failed += 1
        
        if not token:
            print("\n⚠️  Cannot test authenticated endpoints without token")
            print(f"\nTotal Tests: {passed + failed}")
            print(f"Passed: {passed} ✅")
            print(f"Failed: {failed} ❌")
            return False
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test 3: Get Junctions
        print("\n3. Testing Junctions Endpoint...")
        try:
            response = await client.get(f"{API_BASE_URL}/junctions", headers=headers)
            if response.status_code == 200:
                data = response.json()
                junction_count = len(data) if isinstance(data, list) else len(data.get('junctions', []))
                print(f"   ✅ PASS: GET /junctions")
                print(f"      Junctions found: {junction_count}")
                passed += 1
            else:
                print(f"   ❌ FAIL: GET /junctions (Status: {response.status_code})")
                failed += 1
        except Exception as e:
            print(f"   ❌ FAIL: GET /junctions")
            print(f"      Error: {str(e)}")
            failed += 1
        
        # Test 4: Get System State
        print("\n4. Testing System State Endpoint...")
        try:
            response = await client.get(f"{API_BASE_URL}/system/state", headers=headers)
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ PASS: GET /system/state")
                print(f"      Current mode: {data.get('current_mode') or data.get('mode')}")
                passed += 1
            else:
                print(f"   ❌ FAIL: GET /system/state (Status: {response.status_code})")
                failed += 1
        except Exception as e:
            print(f"   ❌ FAIL: GET /system/state")
            print(f"      Error: {str(e)}")
            failed += 1
        
        # Test 5: Get Commands
        print("\n5. Testing Commands Endpoint...")
        try:
            response = await client.get(f"{API_BASE_URL}/commands", headers=headers)
            if response.status_code == 200:
                data = response.json()
                command_count = len(data) if isinstance(data, list) else len(data.get('commands', []))
                print(f"   ✅ PASS: GET /commands")
                print(f"      Commands found: {command_count}")
                passed += 1
            else:
                print(f"   ❌ FAIL: GET /commands (Status: {response.status_code})")
                failed += 1
        except Exception as e:
            print(f"   ❌ FAIL: GET /commands")
            print(f"      Error: {str(e)}")
            failed += 1
        
        # Test 6: Get Junction Stats
        print("\n6. Testing Junction Stats Endpoint...")
        try:
            response = await client.get(f"{API_BASE_URL}/junctions/stats/overview", headers=headers)
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ PASS: GET /junctions/stats/overview")
                print(f"      Total junctions: {data.get('total_junctions', 'N/A')}")
                passed += 1
            else:
                print(f"   ❌ FAIL: GET /junctions/stats/overview (Status: {response.status_code})")
                failed += 1
        except Exception as e:
            print(f"   ❌ FAIL: GET /junctions/stats/overview")
            print(f"      Error: {str(e)}")
            failed += 1
        
        # Test 7: Create Junction (POST)
        print("\n7. Testing Create Junction Endpoint...")
        try:
            test_junction = {
                "name": f"Test Junction API",
                "ip_address": "192.168.1.250",
                "location": "Test Location",
                "zone": "Test Zone"
            }
            response = await client.post(
                f"{API_BASE_URL}/junctions",
                json=test_junction,
                headers=headers
            )
            if response.status_code in [200, 201]:
                data = response.json()
                print(f"   ✅ PASS: POST /junctions")
                print(f"      Created junction ID: {data.get('id')}")
                passed += 1
                
                # Clean up - delete test junction
                junction_id = data.get('id')
                if junction_id:
                    try:
                        await client.delete(
                            f"{API_BASE_URL}/junctions/{junction_id}",
                            headers=headers
                        )
                        print(f"      Cleaned up test junction")
                    except:
                        pass
            else:
                print(f"   ❌ FAIL: POST /junctions (Status: {response.status_code})")
                print(f"      Response: {response.text[:200]}")
                failed += 1
        except Exception as e:
            print(f"   ❌ FAIL: POST /junctions")
            print(f"      Error: {str(e)}")
            failed += 1
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    total = passed + failed
    percentage = (passed / total * 100) if total > 0 else 0
    print(f"\nTotal Tests: {total}")
    print(f"Passed: {passed} ✅")
    print(f"Failed: {failed} ❌")
    print(f"Success Rate: {percentage:.1f}%")
    
    print("\n" + "="*70)
    if failed == 0:
        print("✅ ALL API TESTS PASSED - BACKEND IS PERFECT!")
    else:
        print(f"⚠️  {failed} TEST(S) FAILED")
    print("="*70)
    
    return failed == 0


if __name__ == "__main__":
    success = asyncio.run(test_apis())
    sys.exit(0 if success else 1)
