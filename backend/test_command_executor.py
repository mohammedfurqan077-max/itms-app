"""
Test script for Command Executor System

This script demonstrates the automatic background processing of commands.
"""
import asyncio
import httpx
import json
from datetime import datetime
import time


# Configuration
BASE_URL = "http://localhost:8000/api/v1"
ADMIN_EMAIL = "admin@itms.com"
ADMIN_PASSWORD = "admin123"


class CommandExecutorTester:
    """Test the command executor system"""
    
    def __init__(self):
        self.base_url = BASE_URL
        self.token = None
        self.headers = {}
    
    async def login(self):
        """Login and get access token"""
        print("\n" + "="*80)
        print("STEP 1: Login as admin")
        print("="*80)
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/auth/login",
                data={
                    "username": ADMIN_EMAIL,
                    "password": ADMIN_PASSWORD
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data["access_token"]
                self.headers = {"Authorization": f"Bearer {self.token}"}
                print(f"✓ Login successful")
                print(f"  Token: {self.token[:50]}...")
                return True
            else:
                print(f"✗ Login failed: {response.status_code}")
                print(f"  Response: {response.text}")
                return False
    
    async def create_command(self, command_type: str, payload: dict, execute_immediately: bool = False):
        """
        Create a command
        
        Args:
            command_type: Type of command
            payload: Command payload
            execute_immediately: Execute immediately or queue for background processing
        
        Returns:
            Command ID if successful, None otherwise
        """
        async with httpx.AsyncClient() as client:
            request_data = {
                "junction_id": 1,
                "command_type": command_type,
                "payload": payload,
                "execute_immediately": execute_immediately
            }
            
            response = await client.post(
                f"{self.base_url}/commands/send",
                headers=self.headers,
                json=request_data
            )
            
            if response.status_code == 200:
                data = response.json()
                command_id = data.get("command_id")
                status = data.get("status")
                print(f"  ✓ Command created: ID={command_id}, Status={status}")
                return command_id
            else:
                print(f"  ✗ Failed to create command: {response.status_code}")
                print(f"    Response: {response.text}")
                return None
    
    async def get_command_status(self, command_id: int):
        """Get command status"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/commands/{command_id}",
                headers=self.headers
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"  ✗ Failed to get command status: {response.status_code}")
                return None
    
    async def wait_for_command_completion(self, command_id: int, timeout: int = 30):
        """
        Wait for command to complete
        
        Args:
            command_id: Command ID
            timeout: Maximum wait time in seconds
        
        Returns:
            Final command data or None if timeout
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            command = await self.get_command_status(command_id)
            
            if command:
                status = command.get("status")
                
                # Check if completed
                if status in ["success", "failed", "timeout", "cancelled"]:
                    return command
            
            # Wait before checking again
            await asyncio.sleep(1)
        
        print(f"  ⚠ Timeout waiting for command {command_id} to complete")
        return None
    
    async def test_background_execution(self):
        """Test background command execution"""
        print("\n" + "="*80)
        print("STEP 2: Test Background Command Execution")
        print("="*80)
        print("\nCreating commands with execute_immediately=False")
        print("These commands will be processed by the background executor\n")
        
        test_cases = [
            {
                "name": "GET_STATUS",
                "command_type": "get_status",
                "payload": {}
            },
            {
                "name": "SET_MODE (manual)",
                "command_type": "set_mode",
                "payload": {"mode": "manual"}
            },
            {
                "name": "SET_TIME",
                "command_type": "set_time",
                "payload": {
                    "lane1": 30,
                    "lane2": 45,
                    "lane3": 30,
                    "lane4": 45
                }
            },
            {
                "name": "VIP_MODE (activate)",
                "command_type": "vip_mode",
                "payload": {
                    "active": True,
                    "lanes_to_green": [1, 2]
                }
            },
            {
                "name": "VIP_MODE (deactivate)",
                "command_type": "vip_mode",
                "payload": {
                    "active": False
                }
            }
        ]
        
        command_ids = []
        
        # Create all commands
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n{i}. Creating command: {test_case['name']}")
            print(f"   Type: {test_case['command_type']}")
            print(f"   Payload: {json.dumps(test_case['payload'], indent=2)}")
            
            command_id = await self.create_command(
                command_type=test_case['command_type'],
                payload=test_case['payload'],
                execute_immediately=False  # Queue for background processing
            )
            
            if command_id:
                command_ids.append({
                    "id": command_id,
                    "name": test_case['name'],
                    "type": test_case['command_type']
                })
        
        print(f"\n{'='*80}")
        print(f"Created {len(command_ids)} commands")
        print(f"{'='*80}")
        
        # Wait for all commands to complete
        print("\n" + "="*80)
        print("STEP 3: Monitor Command Execution")
        print("="*80)
        print("\nWaiting for background executor to process commands...")
        print("(Executor polls every 2 seconds)\n")
        
        results = []
        
        for cmd_info in command_ids:
            print(f"\nMonitoring: {cmd_info['name']} (ID: {cmd_info['id']})")
            
            command = await self.wait_for_command_completion(cmd_info['id'], timeout=30)
            
            if command:
                status = command.get("status")
                executed_at = command.get("executed_at")
                completed_at = command.get("completed_at")
                error_message = command.get("error_message")
                
                # Calculate execution time
                exec_time = None
                if executed_at and completed_at:
                    exec_start = datetime.fromisoformat(executed_at.replace('Z', '+00:00'))
                    exec_end = datetime.fromisoformat(completed_at.replace('Z', '+00:00'))
                    exec_time = (exec_end - exec_start).total_seconds()
                
                result = {
                    "name": cmd_info['name'],
                    "id": cmd_info['id'],
                    "status": status,
                    "execution_time": exec_time,
                    "error": error_message
                }
                results.append(result)
                
                if status == "success":
                    print(f"  ✓ Status: {status}")
                    if exec_time:
                        print(f"  ✓ Execution time: {exec_time:.2f}s")
                else:
                    print(f"  ✗ Status: {status}")
                    if error_message:
                        print(f"  ✗ Error: {error_message}")
            else:
                results.append({
                    "name": cmd_info['name'],
                    "id": cmd_info['id'],
                    "status": "timeout",
                    "execution_time": None,
                    "error": "Timeout waiting for completion"
                })
        
        return results
    
    async def print_summary(self, results):
        """Print test summary"""
        print("\n" + "="*80)
        print("STEP 4: Test Summary")
        print("="*80)
        
        total = len(results)
        success = sum(1 for r in results if r["status"] == "success")
        failed = sum(1 for r in results if r["status"] in ["failed", "timeout"])
        
        print(f"\nTotal Commands: {total}")
        print(f"Successful: {success}")
        print(f"Failed: {failed}")
        print(f"Success Rate: {(success/total*100):.1f}%")
        
        print("\n" + "-"*80)
        print("Detailed Results:")
        print("-"*80)
        
        for i, result in enumerate(results, 1):
            status_icon = "✓" if result["status"] == "success" else "✗"
            print(f"\n{i}. {result['name']}")
            print(f"   {status_icon} Status: {result['status']}")
            print(f"   Command ID: {result['id']}")
            
            if result["execution_time"]:
                print(f"   Execution Time: {result['execution_time']:.2f}s")
            
            if result["error"]:
                print(f"   Error: {result['error']}")
        
        print("\n" + "="*80)
        print("Test Complete!")
        print("="*80)
        
        # Note about control system
        if failed > 0:
            print("\nNOTE: Some commands may fail if the control system is not running.")
            print("The control system is expected at http://localhost:5000")
            print("This is normal in a development environment without physical hardware.")
    
    async def run_tests(self):
        """Run all tests"""
        print("\n" + "="*80)
        print("COMMAND EXECUTOR SYSTEM TEST")
        print("="*80)
        print("\nThis test demonstrates automatic background command processing.")
        print("Commands are created with execute_immediately=False and are")
        print("automatically picked up and executed by the background executor.")
        
        # Login
        if not await self.login():
            print("\n✗ Login failed. Cannot proceed with tests.")
            return
        
        # Test background execution
        results = await self.test_background_execution()
        
        # Print summary
        await self.print_summary(results)


async def main():
    """Main test function"""
    tester = CommandExecutorTester()
    await tester.run_tests()


if __name__ == "__main__":
    print("\n" + "="*80)
    print("COMMAND EXECUTOR TEST SCRIPT")
    print("="*80)
    print("\nPrerequisites:")
    print("1. Backend server must be running (python -m uvicorn app.main:app --reload)")
    print("2. Admin account must exist (admin@itms.com / admin123)")
    print("3. At least one junction must exist in database")
    print("\nPress Ctrl+C to cancel, or Enter to continue...")
    
    try:
        input()
    except KeyboardInterrupt:
        print("\n\nTest cancelled.")
        exit(0)
    
    asyncio.run(main())
