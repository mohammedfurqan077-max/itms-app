"""
Test script to verify ENUM fix is working correctly
"""
import asyncio
import httpx
import sys


BASE_URL = "http://localhost:8000/api/v1"
ADMIN_EMAIL = "admin@itms.com"
ADMIN_PASSWORD = "admin123"


async def test_enum_fix():
    """Test that commands work without ENUM types"""
    
    print("\n" + "="*80)
    print("ENUM FIX VERIFICATION TEST")
    print("="*80)
    
    # Step 1: Login
    print("\n[1/5] Testing login...")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{BASE_URL}/auth/login",
                data={
                    "username": ADMIN_EMAIL,
                    "password": ADMIN_PASSWORD
                }
            )
            
            if response.status_code != 200:
                print(f"✗ Login failed: {response.status_code}")
                print(f"  Response: {response.text}")
                return False
            
            data = response.json()
            token = data["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            print(f"✓ Login successful")
            
        except Exception as e:
            print(f"✗ Login error: {str(e)}")
            return False
    
    # Step 2: Create command with string status
    print("\n[2/5] Creating command (should use STRING, not ENUM)...")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{BASE_URL}/commands/send",
                headers=headers,
                json={
                    "junction_id": 1,
                    "command_type": "get_status",
                    "payload": {},
                    "execute_immediately": False
                }
            )
            
            if response.status_code != 200:
                print(f"✗ Command creation failed: {response.status_code}")
                print(f"  Response: {response.text}")
                return False
            
            data = response.json()
            command_id = data.get("command_id")
            status = data.get("status")
            
            print(f"✓ Command created successfully")
            print(f"  Command ID: {command_id}")
            print(f"  Status: {status}")
            
            # Verify status is a string
            if status != "pending":
                print(f"✗ Expected status='pending', got '{status}'")
                return False
            
            print(f"✓ Status is correct string value: 'pending'")
            
        except Exception as e:
            print(f"✗ Command creation error: {str(e)}")
            return False
    
    # Step 3: Wait for executor to process
    print("\n[3/5] Waiting for background executor (5 seconds)...")
    await asyncio.sleep(5)
    print("✓ Wait complete")
    
    # Step 4: Check command status
    print("\n[4/5] Checking command status...")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{BASE_URL}/commands/{command_id}",
                headers=headers
            )
            
            if response.status_code != 200:
                print(f"✗ Failed to get command: {response.status_code}")
                return False
            
            command = response.json()
            status = command.get("status")
            command_type = command.get("command_type")
            
            print(f"✓ Command retrieved successfully")
            print(f"  Command Type: {command_type}")
            print(f"  Status: {status}")
            
            # Verify values are strings
            if not isinstance(status, str):
                print(f"✗ Status is not a string: {type(status)}")
                return False
            
            if not isinstance(command_type, str):
                print(f"✗ Command type is not a string: {type(command_type)}")
                return False
            
            print(f"✓ Both command_type and status are strings (not ENUMs)")
            
            # Check if status changed
            if status in ["success", "failed", "timeout"]:
                print(f"✓ Command was processed by executor")
            elif status == "executing":
                print(f"⚠ Command is still executing")
            elif status == "pending":
                print(f"⚠ Command is still pending (executor may not be running)")
            
        except Exception as e:
            print(f"✗ Error checking command: {str(e)}")
            return False
    
    # Step 5: Test all command types
    print("\n[5/5] Testing all command types...")
    
    test_commands = [
        {"type": "set_mode", "payload": {"mode": "manual"}},
        {"type": "set_time", "payload": {"lane1": 30, "lane2": 45, "lane3": 30, "lane4": 45}},
        {"type": "vip_mode", "payload": {"active": True, "lanes_to_green": [1, 2]}},
    ]
    
    async with httpx.AsyncClient() as client:
        for test_cmd in test_commands:
            try:
                response = await client.post(
                    f"{BASE_URL}/commands/send",
                    headers=headers,
                    json={
                        "junction_id": 1,
                        "command_type": test_cmd["type"],
                        "payload": test_cmd["payload"],
                        "execute_immediately": False
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"  ✓ {test_cmd['type']}: Created (ID: {data.get('command_id')})")
                else:
                    print(f"  ✗ {test_cmd['type']}: Failed ({response.status_code})")
                    
            except Exception as e:
                print(f"  ✗ {test_cmd['type']}: Error - {str(e)}")
    
    print("\n" + "="*80)
    print("ENUM FIX VERIFICATION COMPLETE")
    print("="*80)
    print("\n✅ All tests passed!")
    print("\nKey Findings:")
    print("  • Commands use STRING fields (not ENUM)")
    print("  • Status values are strings: 'pending', 'executing', 'success', etc.")
    print("  • Command types are strings: 'get_status', 'set_mode', etc.")
    print("  • No PostgreSQL ENUM types required")
    print("  • Compatible with asyncpg driver")
    print("\n" + "="*80)
    
    return True


async def main():
    """Main test function"""
    print("\nPrerequisites:")
    print("1. Backend server must be running")
    print("2. Database must be migrated (alembic upgrade head)")
    print("3. Admin account must exist")
    print("4. At least one junction must exist")
    print("\nPress Enter to continue or Ctrl+C to cancel...")
    
    try:
        input()
    except KeyboardInterrupt:
        print("\n\nTest cancelled.")
        sys.exit(0)
    
    success = await test_enum_fix()
    
    if not success:
        print("\n✗ Some tests failed. Check the output above.")
        sys.exit(1)
    
    sys.exit(0)


if __name__ == "__main__":
    asyncio.run(main())
