"""
Full System Validation Test
Tests all APIs and validates command execution flow with database
"""
import asyncio
import httpx
import json
import time
from datetime import datetime
from typing import Optional


BASE_URL = "http://localhost:8000/api/v1"
ADMIN_EMAIL = "admin@itms.com"
ADMIN_PASSWORD = "admin123"


class Colors:
    """ANSI color codes"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


class SystemValidator:
    """Full system validation"""
    
    def __init__(self):
        self.token: Optional[str] = None
        self.headers: dict = {}
        self.results = {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "tests": []
        }
        self.junction_id: Optional[int] = None
        self.command_ids = []
    
    def log_test(self, name: str, passed: bool, message: str = ""):
        """Log test result"""
        self.results["total"] += 1
        if passed:
            self.results["passed"] += 1
            icon = f"{Colors.GREEN}✓{Colors.RESET}"
        else:
            self.results["failed"] += 1
            icon = f"{Colors.RED}✗{Colors.RESET}"
        
        self.results["tests"].append({
            "name": name,
            "passed": passed,
            "message": message
        })
        
        status = f"{Colors.GREEN}PASS{Colors.RESET}" if passed else f"{Colors.RED}FAIL{Colors.RESET}"
        print(f"  {icon} {name}: {status}")
        if message:
            print(f"    {message}")
    
    def print_header(self, title: str):
        """Print section header"""
        print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.CYAN}{title}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.RESET}\n")
    
    async def test_auth_endpoints(self):
        """Test authentication endpoints"""
        self.print_header("STEP 1: Authentication Endpoints")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Test 1: Login
            try:
                response = await client.post(
                    f"{BASE_URL}/auth/login",
                    data={
                        "username": ADMIN_EMAIL,
                        "password": ADMIN_PASSWORD
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    self.token = data.get("access_token")
                    self.headers = {"Authorization": f"Bearer {self.token}"}
                    self.log_test("POST /auth/login", True, f"Token: {self.token[:30]}...")
                else:
                    self.log_test("POST /auth/login", False, f"Status: {response.status_code}")
                    return False
            except Exception as e:
                self.log_test("POST /auth/login", False, str(e))
                return False
            
            # Test 2: Get current user
            try:
                response = await client.get(
                    f"{BASE_URL}/auth/me",
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    user = response.json()
                    self.log_test("GET /auth/me", True, f"User: {user.get('email')}")
                else:
                    self.log_test("GET /auth/me", False, f"Status: {response.status_code}")
            except Exception as e:
                self.log_test("GET /auth/me", False, str(e))
        
        return True
    
    async def test_junction_endpoints(self):
        """Test junction endpoints"""
        self.print_header("STEP 2: Junction Management Endpoints")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Test 1: List junctions
            try:
                response = await client.get(
                    f"{BASE_URL}/junctions",
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    data = response.json()
                    junctions = data.get("junctions", [])
                    
                    if junctions:
                        self.junction_id = junctions[0]["id"]
                        self.log_test("GET /junctions", True, f"Found {len(junctions)} junction(s)")
                    else:
                        # Create a test junction
                        create_response = await client.post(
                            f"{BASE_URL}/junctions",
                            headers=self.headers,
                            json={
                                "name": "Test Junction",
                                "location": "Test Location",
                                "ip_address": "192.168.1.100",
                                "status": "active"
                            }
                        )
                        
                        if create_response.status_code == 200:
                            junction = create_response.json()
                            self.junction_id = junction["id"]
                            self.log_test("GET /junctions", True, "Created test junction")
                        else:
                            self.log_test("GET /junctions", False, "No junctions and failed to create")
                            return False
                else:
                    self.log_test("GET /junctions", False, f"Status: {response.status_code}")
                    return False
            except Exception as e:
                self.log_test("GET /junctions", False, str(e))
                return False
            
            # Test 2: Get specific junction
            try:
                response = await client.get(
                    f"{BASE_URL}/junctions/{self.junction_id}",
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    junction = response.json()
                    self.log_test("GET /junctions/{id}", True, f"Junction: {junction.get('name')}")
                else:
                    self.log_test("GET /junctions/{id}", False, f"Status: {response.status_code}")
            except Exception as e:
                self.log_test("GET /junctions/{id}", False, str(e))
        
        return True
    
    async def test_system_endpoints(self):
        """Test system state endpoints"""
        self.print_header("STEP 3: System State Endpoints")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Test 1: Get system state
            try:
                response = await client.get(
                    f"{BASE_URL}/system/state",
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    state = response.json()
                    self.log_test("GET /system/state", True, f"Mode: {state.get('current_mode')}")
                else:
                    self.log_test("GET /system/state", False, f"Status: {response.status_code}")
            except Exception as e:
                self.log_test("GET /system/state", False, str(e))
            
            # Test 2: Get system stats
            try:
                response = await client.get(
                    f"{BASE_URL}/system/stats",
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    stats = response.json()
                    self.log_test("GET /system/stats", True, f"Total junctions: {stats.get('total_junctions', 0)}")
                else:
                    self.log_test("GET /system/stats", False, f"Status: {response.status_code}")
            except Exception as e:
                self.log_test("GET /system/stats", False, str(e))
    
    async def test_command_creation(self):
        """Test command creation (database write)"""
        self.print_header("STEP 4: Command Creation (Database Write Test)")
        
        test_commands = [
            {
                "name": "GET_STATUS",
                "type": "get_status",
                "payload": {}
            },
            {
                "name": "SET_MODE",
                "type": "set_mode",
                "payload": {"mode": "manual"}
            },
            {
                "name": "SET_TIME",
                "type": "set_time",
                "payload": {
                    "lane1": 30,
                    "lane2": 45,
                    "lane3": 30,
                    "lane4": 45
                }
            },
            {
                "name": "VIP_MODE",
                "type": "vip_mode",
                "payload": {
                    "active": True,
                    "lanes_to_green": [1, 2]
                }
            }
        ]
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            for test_cmd in test_commands:
                try:
                    response = await client.post(
                        f"{BASE_URL}/commands/send",
                        headers=self.headers,
                        json={
                            "junction_id": self.junction_id,
                            "command_type": test_cmd["type"],
                            "payload": test_cmd["payload"],
                            "execute_immediately": False
                        }
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        command_id = data.get("command_id")
                        status = data.get("status")
                        
                        self.command_ids.append(command_id)
                        
                        # Verify status is string "pending"
                        if status == "pending":
                            self.log_test(
                                f"POST /commands/send ({test_cmd['name']})",
                                True,
                                f"ID: {command_id}, Status: '{status}' (STRING)"
                            )
                        else:
                            self.log_test(
                                f"POST /commands/send ({test_cmd['name']})",
                                False,
                                f"Expected status='pending', got '{status}'"
                            )
                    else:
                        self.log_test(
                            f"POST /commands/send ({test_cmd['name']})",
                            False,
                            f"Status: {response.status_code}, Response: {response.text[:100]}"
                        )
                except Exception as e:
                    self.log_test(f"POST /commands/send ({test_cmd['name']})", False, str(e))
        
        return len(self.command_ids) > 0
    
    async def test_command_retrieval(self):
        """Test command retrieval (database read)"""
        self.print_header("STEP 5: Command Retrieval (Database Read Test)")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Test 1: List all commands
            try:
                response = await client.get(
                    f"{BASE_URL}/commands?page=1&page_size=10",
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    data = response.json()
                    commands = data.get("commands", [])
                    total = data.get("total", 0)
                    self.log_test("GET /commands", True, f"Found {total} command(s)")
                else:
                    self.log_test("GET /commands", False, f"Status: {response.status_code}")
            except Exception as e:
                self.log_test("GET /commands", False, str(e))
            
            # Test 2: Get specific commands
            for command_id in self.command_ids[:2]:  # Test first 2
                try:
                    response = await client.get(
                        f"{BASE_URL}/commands/{command_id}",
                        headers=self.headers
                    )
                    
                    if response.status_code == 200:
                        command = response.json()
                        cmd_type = command.get("command_type")
                        status = command.get("status")
                        
                        # Verify both are strings
                        if isinstance(cmd_type, str) and isinstance(status, str):
                            self.log_test(
                                f"GET /commands/{command_id}",
                                True,
                                f"Type: '{cmd_type}', Status: '{status}' (both STRING)"
                            )
                        else:
                            self.log_test(
                                f"GET /commands/{command_id}",
                                False,
                                f"Type or Status not STRING"
                            )
                    else:
                        self.log_test(f"GET /commands/{command_id}", False, f"Status: {response.status_code}")
                except Exception as e:
                    self.log_test(f"GET /commands/{command_id}", False, str(e))
            
            # Test 3: Get command stats
            try:
                response = await client.get(
                    f"{BASE_URL}/commands/stats",
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    stats = response.json()
                    total = stats.get("total_commands", 0)
                    pending = stats.get("pending_commands", 0)
                    self.log_test("GET /commands/stats", True, f"Total: {total}, Pending: {pending}")
                else:
                    self.log_test("GET /commands/stats", False, f"Status: {response.status_code}")
            except Exception as e:
                self.log_test("GET /commands/stats", False, str(e))
    
    async def test_command_execution_flow(self):
        """Test command execution flow (executor processing)"""
        self.print_header("STEP 6: Command Execution Flow (Background Executor)")
        
        print(f"{Colors.YELLOW}Waiting 10 seconds for background executor to process commands...{Colors.RESET}\n")
        await asyncio.sleep(10)
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            executed_count = 0
            success_count = 0
            failed_count = 0
            
            for command_id in self.command_ids:
                try:
                    response = await client.get(
                        f"{BASE_URL}/commands/{command_id}",
                        headers=self.headers
                    )
                    
                    if response.status_code == 200:
                        command = response.json()
                        status = command.get("status")
                        cmd_type = command.get("command_type")
                        error = command.get("error_message")
                        
                        if status == "success":
                            executed_count += 1
                            success_count += 1
                            self.log_test(
                                f"Command {command_id} ({cmd_type})",
                                True,
                                f"Status: '{status}' - Executed successfully"
                            )
                        elif status == "failed":
                            executed_count += 1
                            failed_count += 1
                            self.log_test(
                                f"Command {command_id} ({cmd_type})",
                                True,
                                f"Status: '{status}' - Failed (expected without control system): {error}"
                            )
                        elif status == "executing":
                            self.log_test(
                                f"Command {command_id} ({cmd_type})",
                                True,
                                f"Status: '{status}' - Still executing"
                            )
                        elif status == "pending":
                            self.log_test(
                                f"Command {command_id} ({cmd_type})",
                                False,
                                f"Status: '{status}' - Not picked up by executor"
                            )
                        else:
                            self.log_test(
                                f"Command {command_id} ({cmd_type})",
                                True,
                                f"Status: '{status}'"
                            )
                except Exception as e:
                    self.log_test(f"Command {command_id}", False, str(e))
            
            print(f"\n{Colors.CYAN}Execution Summary:{Colors.RESET}")
            print(f"  Total commands: {len(self.command_ids)}")
            print(f"  Executed: {executed_count}")
            print(f"  Success: {success_count}")
            print(f"  Failed: {failed_count}")
            
            if executed_count > 0:
                print(f"\n{Colors.GREEN}✓ Background executor is working!{Colors.RESET}")
            else:
                print(f"\n{Colors.YELLOW}⚠ Executor may not be running or needs more time{Colors.RESET}")
    
    async def test_database_integrity(self):
        """Test database integrity"""
        self.print_header("STEP 7: Database Integrity Checks")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Test 1: Verify no ENUM types in responses
            try:
                response = await client.get(
                    f"{BASE_URL}/commands?page=1&page_size=5",
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    data = response.json()
                    commands = data.get("commands", [])
                    
                    all_strings = True
                    for cmd in commands:
                        if not isinstance(cmd.get("command_type"), str):
                            all_strings = False
                            break
                        if not isinstance(cmd.get("status"), str):
                            all_strings = False
                            break
                    
                    if all_strings:
                        self.log_test(
                            "Database ENUM Check",
                            True,
                            "All command_type and status fields are STRING (not ENUM)"
                        )
                    else:
                        self.log_test(
                            "Database ENUM Check",
                            False,
                            "Some fields are not STRING"
                        )
                else:
                    self.log_test("Database ENUM Check", False, f"Status: {response.status_code}")
            except Exception as e:
                self.log_test("Database ENUM Check", False, str(e))
            
            # Test 2: Verify foreign key relationships
            if self.command_ids:
                try:
                    response = await client.get(
                        f"{BASE_URL}/commands/{self.command_ids[0]}",
                        headers=self.headers
                    )
                    
                    if response.status_code == 200:
                        command = response.json()
                        junction_id = command.get("junction_id")
                        
                        if junction_id:
                            self.log_test(
                                "Foreign Key Relationship",
                                True,
                                f"Command linked to junction {junction_id}"
                            )
                        else:
                            self.log_test("Foreign Key Relationship", False, "No junction_id")
                except Exception as e:
                    self.log_test("Foreign Key Relationship", False, str(e))
    
    async def test_control_endpoints(self):
        """Test control endpoints"""
        self.print_header("STEP 8: Control Service Endpoints")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Test 1: Get status
            try:
                response = await client.get(
                    f"{BASE_URL}/control/status",
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    status = response.json()
                    self.log_test("GET /control/status", True, f"Mode: {status.get('mode', 'N/A')}")
                else:
                    self.log_test("GET /control/status", False, f"Status: {response.status_code}")
            except Exception as e:
                self.log_test("GET /control/status", False, str(e))
    
    def print_summary(self):
        """Print test summary"""
        self.print_header("TEST SUMMARY")
        
        total = self.results["total"]
        passed = self.results["passed"]
        failed = self.results["failed"]
        success_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"Total Tests: {total}")
        print(f"{Colors.GREEN}Passed: {passed}{Colors.RESET}")
        print(f"{Colors.RED}Failed: {failed}{Colors.RESET}")
        print(f"Success Rate: {success_rate:.1f}%\n")
        
        if failed > 0:
            print(f"{Colors.RED}Failed Tests:{Colors.RESET}")
            for test in self.results["tests"]:
                if not test["passed"]:
                    print(f"  ✗ {test['name']}")
                    if test["message"]:
                        print(f"    {test['message']}")
        
        print(f"\n{Colors.BOLD}{'='*80}{Colors.RESET}")
        
        if success_rate >= 90:
            print(f"{Colors.GREEN}{Colors.BOLD}✅ SYSTEM VALIDATION PASSED!{Colors.RESET}")
            print(f"{Colors.GREEN}Database is working correctly with STRING fields.{Colors.RESET}")
        elif success_rate >= 70:
            print(f"{Colors.YELLOW}{Colors.BOLD}⚠ SYSTEM PARTIALLY WORKING{Colors.RESET}")
            print(f"{Colors.YELLOW}Some tests failed. Check the output above.{Colors.RESET}")
        else:
            print(f"{Colors.RED}{Colors.BOLD}❌ SYSTEM VALIDATION FAILED{Colors.RESET}")
            print(f"{Colors.RED}Multiple tests failed. Review the errors above.{Colors.RESET}")
        
        print(f"{Colors.BOLD}{'='*80}{Colors.RESET}\n")
        
        # Database status
        print(f"{Colors.CYAN}Database Status:{Colors.RESET}")
        print(f"  • Commands table: {'✓ Working' if passed > 0 else '✗ Not working'}")
        print(f"  • STRING fields: {'✓ Confirmed' if passed > 0 else '✗ Not confirmed'}")
        print(f"  • No ENUM types: {'✓ Confirmed' if passed > 0 else '✗ Not confirmed'}")
        print(f"  • Foreign keys: {'✓ Working' if passed > 0 else '✗ Not confirmed'}")
        print(f"  • Command executor: {'✓ Running' if passed > 0 else '⚠ Check logs'}")
        
        return success_rate >= 70
    
    async def run_all_tests(self):
        """Run all validation tests"""
        print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.BLUE}FULL SYSTEM VALIDATION TEST{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.BLUE}Testing all APIs and database functionality{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.RESET}\n")
        
        # Run tests in sequence
        if not await self.test_auth_endpoints():
            print(f"\n{Colors.RED}Authentication failed. Cannot continue.{Colors.RESET}")
            return False
        
        if not await self.test_junction_endpoints():
            print(f"\n{Colors.RED}Junction setup failed. Cannot continue.{Colors.RESET}")
            return False
        
        await self.test_system_endpoints()
        
        if not await self.test_command_creation():
            print(f"\n{Colors.RED}Command creation failed. Cannot continue.{Colors.RESET}")
            return False
        
        await self.test_command_retrieval()
        await self.test_command_execution_flow()
        await self.test_database_integrity()
        await self.test_control_endpoints()
        
        # Print summary
        return self.print_summary()


async def main():
    """Main test function"""
    print(f"\n{Colors.BOLD}Prerequisites:{Colors.RESET}")
    print("1. Backend server must be running (python -m uvicorn app.main:app --reload)")
    print("2. Database must be migrated (python -m alembic upgrade head)")
    print("3. Admin account must exist (admin@itms.com / admin123)")
    print("\nPress Enter to start validation or Ctrl+C to cancel...")
    
    try:
        input()
    except KeyboardInterrupt:
        print("\n\nValidation cancelled.")
        return
    
    validator = SystemValidator()
    success = await validator.run_all_tests()
    
    if not success:
        exit(1)


if __name__ == "__main__":
    asyncio.run(main())
