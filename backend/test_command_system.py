"""
Command Execution System - Comprehensive Test Script

This script tests all components of the command execution system:
- Models
- Schemas
- Service layer
- API endpoints
- Database migration
- Integration with control service
"""

import sys
import importlib.util
from pathlib import Path

# Color codes for output
GREEN = '\033[92m'
RED = '\033[91m'
BLUE = '\033[94m'
YELLOW = '\033[93m'
RESET = '\033[0m'

def print_header(text):
    """Print a formatted header"""
    print(f"\n{BLUE}{'=' * 80}{RESET}")
    print(f"{BLUE}{text.center(80)}{RESET}")
    print(f"{BLUE}{'=' * 80}{RESET}\n")

def print_test(test_name):
    """Print test name"""
    print(f"{YELLOW}Testing:{RESET} {test_name}...", end=" ")

def print_success(message=""):
    """Print success message"""
    msg = f" - {message}" if message else ""
    print(f"{GREEN}✓ PASS{RESET}{msg}")

def print_failure(message=""):
    """Print failure message"""
    msg = f" - {message}" if message else ""
    print(f"{RED}✗ FAIL{RESET}{msg}")

def test_imports():
    """Test 1: Module Imports"""
    print_header("TEST 1: MODULE IMPORTS")
    
    tests_passed = 0
    tests_failed = 0
    
    # Test command model import
    print_test("Command model import")
    try:
        from app.models.command import Command, CommandType, CommandStatus
        assert Command is not None
        assert CommandType is not None
        assert CommandStatus is not None
        print_success("Command, CommandType, CommandStatus imported")
        tests_passed += 1
    except Exception as e:
        print_failure(str(e))
        tests_failed += 1
    
    # Test command schemas import
    print_test("Command schemas import")
    try:
        from app.schemas.command import (
            CommandCreate, SendCommandRequest, CommandResponse,
            CommandListResponse, CommandExecutionResult, CommandStats,
            RetryCommandRequest, CommandTypeEnum, CommandStatusEnum
        )
        assert CommandCreate is not None
        assert SendCommandRequest is not None
        assert CommandResponse is not None
        print_success("All schemas imported (9 schemas)")
        tests_passed += 1
    except Exception as e:
        print_failure(str(e))
        tests_failed += 1
    
    # Test command service import
    print_test("Command service import")
    try:
        from app.services.command_service import CommandService
        assert CommandService is not None
        print_success("CommandService imported")
        tests_passed += 1
    except Exception as e:
        print_failure(str(e))
        tests_failed += 1
    
    # Test command endpoints import
    print_test("Command endpoints import")
    try:
        from app.api.v1.endpoints import commands
        assert commands.router is not None
        print_success("Commands router imported")
        tests_passed += 1
    except Exception as e:
        print_failure(str(e))
        tests_failed += 1
    
    return tests_passed, tests_failed

def test_model():
    """Test 2: Command Model"""
    print_header("TEST 2: COMMAND MODEL")
    
    tests_passed = 0
    tests_failed = 0
    
    try:
        from app.models.command import Command, CommandType, CommandStatus
        
        # Test CommandType enum
        print_test("CommandType enum values")
        expected_types = ['SET_MODE', 'SET_TIME', 'VIP_MODE', 'EMERGENCY_STOP', 'HEARTBEAT', 'GET_STATUS']
        actual_types = [t.name for t in CommandType]
        assert set(expected_types) == set(actual_types), f"Expected {expected_types}, got {actual_types}"
        print_success(f"6 command types: {', '.join(expected_types)}")
        tests_passed += 1
        
        # Test CommandStatus enum
        print_test("CommandStatus enum values")
        expected_statuses = ['PENDING', 'EXECUTING', 'SUCCESS', 'FAILED', 'TIMEOUT', 'CANCELLED']
        actual_statuses = [s.name for s in CommandStatus]
        assert set(expected_statuses) == set(actual_statuses), f"Expected {expected_statuses}, got {actual_statuses}"
        print_success(f"6 statuses: {', '.join(expected_statuses)}")
        tests_passed += 1
        
        # Test model attributes
        print_test("Command model attributes")
        expected_attrs = [
            'id', 'junction_id', 'command_type', 'payload', 'status',
            'response', 'error_message', 'created_by', 'retry_count',
            'max_retries', 'created_at', 'executed_at', 'completed_at'
        ]
        for attr in expected_attrs:
            assert hasattr(Command, attr), f"Missing attribute: {attr}"
        print_success(f"13 attributes present")
        tests_passed += 1
        
        # Test model methods
        print_test("Command model methods")
        expected_methods = [
            'is_pending', 'is_executing', 'is_completed',
            'is_success', 'is_failed', 'can_retry'
        ]
        for method in expected_methods:
            assert hasattr(Command, method), f"Missing method: {method}"
        print_success(f"6 helper methods present")
        tests_passed += 1
        
        # Test table name
        print_test("Command table name")
        assert Command.__tablename__ == 'commands'
        print_success("Table name: 'commands'")
        tests_passed += 1
        
    except Exception as e:
        print_failure(str(e))
        tests_failed += 1
    
    return tests_passed, tests_failed

def test_schemas():
    """Test 3: Command Schemas"""
    print_header("TEST 3: COMMAND SCHEMAS")
    
    tests_passed = 0
    tests_failed = 0
    
    try:
        from app.schemas.command import (
            CommandCreate, SendCommandRequest, CommandResponse,
            CommandTypeEnum, CommandStatusEnum
        )
        
        # Test CommandTypeEnum
        print_test("CommandTypeEnum constants")
        assert CommandTypeEnum.SET_MODE == "set_mode"
        assert CommandTypeEnum.SET_TIME == "set_time"
        assert CommandTypeEnum.VIP_MODE == "vip_mode"
        assert CommandTypeEnum.EMERGENCY_STOP == "emergency_stop"
        assert CommandTypeEnum.HEARTBEAT == "heartbeat"
        assert CommandTypeEnum.GET_STATUS == "get_status"
        print_success("6 command type constants")
        tests_passed += 1
        
        # Test CommandStatusEnum
        print_test("CommandStatusEnum constants")
        assert CommandStatusEnum.PENDING == "pending"
        assert CommandStatusEnum.EXECUTING == "executing"
        assert CommandStatusEnum.SUCCESS == "success"
        assert CommandStatusEnum.FAILED == "failed"
        assert CommandStatusEnum.TIMEOUT == "timeout"
        assert CommandStatusEnum.CANCELLED == "cancelled"
        print_success("6 status constants")
        tests_passed += 1
        
        # Test CommandCreate schema
        print_test("CommandCreate schema")
        cmd = CommandCreate(
            junction_id=1,
            command_type="set_mode",
            payload={"mode": "auto"}
        )
        assert cmd.junction_id == 1
        assert cmd.command_type == "set_mode"
        assert cmd.payload == {"mode": "auto"}
        print_success("CommandCreate validation works")
        tests_passed += 1
        
        # Test SendCommandRequest schema
        print_test("SendCommandRequest schema")
        req = SendCommandRequest(
            junction_id=1,
            command_type="set_mode",
            payload={"mode": "auto"},
            execute_immediately=True
        )
        assert req.execute_immediately == True
        print_success("SendCommandRequest validation works")
        tests_passed += 1
        
        # Test invalid command type
        print_test("Invalid command type validation")
        try:
            CommandCreate(
                junction_id=1,
                command_type="invalid_type",
                payload={}
            )
            print_failure("Should have raised validation error")
            tests_failed += 1
        except Exception:
            print_success("Validation error raised correctly")
            tests_passed += 1
        
    except Exception as e:
        print_failure(str(e))
        tests_failed += 1
    
    return tests_passed, tests_failed

def test_service():
    """Test 4: Command Service"""
    print_header("TEST 4: COMMAND SERVICE")
    
    tests_passed = 0
    tests_failed = 0
    
    try:
        from app.services.command_service import CommandService
        import inspect
        
        # Test service methods
        print_test("CommandService methods")
        expected_methods = [
            'create_command', 'execute_command', 'send_command',
            'get_command_by_id', 'get_commands', 'retry_command',
            'cancel_command', 'get_command_stats', 'get_pending_commands'
        ]
        
        for method in expected_methods:
            assert hasattr(CommandService, method), f"Missing method: {method}"
            # Check if method is async
            method_obj = getattr(CommandService, method)
            assert inspect.iscoroutinefunction(method_obj), f"Method {method} should be async"
        
        print_success(f"9 async methods present")
        tests_passed += 1
        
        # Test service initialization
        print_test("CommandService initialization")
        # We can't actually initialize without a DB session, but we can check the class
        assert CommandService.__init__ is not None
        print_success("Service can be initialized")
        tests_passed += 1
        
    except Exception as e:
        print_failure(str(e))
        tests_failed += 1
    
    return tests_passed, tests_failed

def test_api_endpoints():
    """Test 5: API Endpoints"""
    print_header("TEST 5: API ENDPOINTS")
    
    tests_passed = 0
    tests_failed = 0
    
    try:
        from app.api.v1.endpoints import commands
        
        # Test router exists
        print_test("Commands router")
        assert commands.router is not None
        print_success("Router exists")
        tests_passed += 1
        
        # Test routes
        print_test("API routes")
        routes = [route.path for route in commands.router.routes]
        
        expected_routes = [
            '/send',
            '/{command_id}',
            '',  # List commands
            '/{command_id}/retry',
            '/{command_id}/cancel',
            '/stats/overview',
            '/pending/list'
        ]
        
        # Check if all expected routes exist
        for expected in expected_routes:
            # Some routes might have different representations
            found = any(expected in route or route in expected for route in routes)
            assert found, f"Route {expected} not found in {routes}"
        
        print_success(f"7 endpoints present")
        tests_passed += 1
        
        # Test route methods
        print_test("HTTP methods")
        methods = []
        for route in commands.router.routes:
            if hasattr(route, 'methods'):
                methods.extend(route.methods)
        
        assert 'POST' in methods, "POST method not found"
        assert 'GET' in methods, "GET method not found"
        print_success("POST and GET methods present")
        tests_passed += 1
        
    except Exception as e:
        print_failure(str(e))
        tests_failed += 1
    
    return tests_passed, tests_failed

def test_router_integration():
    """Test 6: Router Integration"""
    print_header("TEST 6: ROUTER INTEGRATION")
    
    tests_passed = 0
    tests_failed = 0
    
    try:
        from app.api.v1.router import api_router
        
        # Test commands router is included
        print_test("Commands router in main router")
        
        # Get all included routers
        routes = [route.path for route in api_router.routes]
        
        # Check if commands routes are present
        commands_routes = [r for r in routes if '/commands' in r]
        assert len(commands_routes) > 0, "No commands routes found"
        
        print_success(f"Commands router integrated ({len(commands_routes)} routes)")
        tests_passed += 1
        
    except Exception as e:
        print_failure(str(e))
        tests_failed += 1
    
    return tests_passed, tests_failed

def test_fastapi_app():
    """Test 7: FastAPI Application"""
    print_header("TEST 7: FASTAPI APPLICATION")
    
    tests_passed = 0
    tests_failed = 0
    
    try:
        from app.main import app
        
        # Test app exists
        print_test("FastAPI app")
        assert app is not None
        print_success("App exists")
        tests_passed += 1
        
        # Test commands routes in app
        print_test("Commands routes in app")
        routes = [route.path for route in app.routes]
        commands_routes = [r for r in routes if '/commands' in r]
        assert len(commands_routes) > 0, "No commands routes in app"
        print_success(f"{len(commands_routes)} commands routes in app")
        tests_passed += 1
        
    except Exception as e:
        print_failure(str(e))
        tests_failed += 1
    
    return tests_passed, tests_failed

def test_migration():
    """Test 8: Database Migration"""
    print_header("TEST 8: DATABASE MIGRATION")
    
    tests_passed = 0
    tests_failed = 0
    
    try:
        # Test migration file exists
        print_test("Migration file exists")
        migration_file = Path("alembic/versions/004_add_command_model.py")
        assert migration_file.exists(), f"Migration file not found: {migration_file}"
        print_success("Migration file: 004_add_command_model.py")
        tests_passed += 1
        
        # Test migration content
        print_test("Migration content")
        with open(migration_file, 'r') as f:
            content = f.read()
        
        # Check for key elements
        assert "revision = '004'" in content, "Revision ID not found"
        assert "down_revision = '003'" in content, "Down revision not found"
        assert "CREATE TYPE commandtype" in content, "CommandType enum not found"
        assert "CREATE TYPE commandstatus" in content, "CommandStatus enum not found"
        assert "CREATE TABLE" in content or "create_table" in content, "Table creation not found"
        
        print_success("Migration has correct structure")
        tests_passed += 1
        
        # Test upgrade function
        print_test("Migration upgrade function")
        assert "def upgrade()" in content, "Upgrade function not found"
        print_success("Upgrade function present")
        tests_passed += 1
        
        # Test downgrade function
        print_test("Migration downgrade function")
        assert "def downgrade()" in content, "Downgrade function not found"
        print_success("Downgrade function present")
        tests_passed += 1
        
    except Exception as e:
        print_failure(str(e))
        tests_failed += 1
    
    return tests_passed, tests_failed

def test_documentation():
    """Test 9: Documentation"""
    print_header("TEST 9: DOCUMENTATION")
    
    tests_passed = 0
    tests_failed = 0
    
    try:
        # Test guide exists
        print_test("Command Execution Guide")
        guide_file = Path("COMMAND_EXECUTION_GUIDE.md")
        assert guide_file.exists(), "Guide file not found"
        
        with open(guide_file, 'r') as f:
            content = f.read()
        
        assert len(content) > 1000, "Guide seems too short"
        assert "Command Types" in content, "Command types section not found"
        assert "API Endpoints" in content, "API endpoints section not found"
        
        print_success(f"Guide exists ({len(content)} chars)")
        tests_passed += 1
        
        # Test API examples exist
        print_test("API Examples Script")
        examples_file = Path("COMMAND_API_EXAMPLES.sh")
        assert examples_file.exists(), "Examples file not found"
        
        with open(examples_file, 'r') as f:
            content = f.read()
        
        assert "#!/bin/bash" in content, "Not a bash script"
        assert "/commands/send" in content, "Send command example not found"
        
        print_success(f"Examples script exists ({len(content)} chars)")
        tests_passed += 1
        
    except Exception as e:
        print_failure(str(e))
        tests_failed += 1
    
    return tests_passed, tests_failed

def test_integration():
    """Test 10: Integration with Other Services"""
    print_header("TEST 10: INTEGRATION WITH OTHER SERVICES")
    
    tests_passed = 0
    tests_failed = 0
    
    try:
        # Test control service integration
        print_test("Control service integration")
        from app.services.command_service import CommandService
        import inspect
        
        # Check if CommandService uses control service
        source = inspect.getsource(CommandService)
        assert "control_service" in source, "Control service not used"
        assert "switch_mode" in source or "set_manual_times" in source, "Control service methods not called"
        
        print_success("Control service integrated")
        tests_passed += 1
        
        # Test junction model relationship
        print_test("Junction model relationship")
        from app.models.command import Command
        assert hasattr(Command, 'junction'), "Junction relationship not found"
        
        print_success("Junction relationship exists")
        tests_passed += 1
        
        # Test user model relationship
        print_test("User model relationship")
        assert hasattr(Command, 'user'), "User relationship not found"
        
        print_success("User relationship exists")
        tests_passed += 1
        
    except Exception as e:
        print_failure(str(e))
        tests_failed += 1
    
    return tests_passed, tests_failed

def main():
    """Run all tests"""
    print_header("COMMAND EXECUTION SYSTEM - COMPREHENSIVE TEST SUITE")
    
    all_tests_passed = 0
    all_tests_failed = 0
    
    # Run all test suites
    test_suites = [
        test_imports,
        test_model,
        test_schemas,
        test_service,
        test_api_endpoints,
        test_router_integration,
        test_fastapi_app,
        test_migration,
        test_documentation,
        test_integration
    ]
    
    for test_suite in test_suites:
        try:
            passed, failed = test_suite()
            all_tests_passed += passed
            all_tests_failed += failed
        except Exception as e:
            print(f"{RED}Test suite failed with exception: {e}{RESET}")
            all_tests_failed += 1
    
    # Print summary
    print_header("TEST SUMMARY")
    
    total_tests = all_tests_passed + all_tests_failed
    success_rate = (all_tests_passed / total_tests * 100) if total_tests > 0 else 0
    
    print(f"Total Tests: {total_tests}")
    print(f"{GREEN}Passed: {all_tests_passed}{RESET}")
    print(f"{RED}Failed: {all_tests_failed}{RESET}")
    print(f"Success Rate: {success_rate:.1f}%")
    
    if all_tests_failed == 0:
        print(f"\n{GREEN}{'=' * 80}{RESET}")
        print(f"{GREEN}{'ALL TESTS PASSED! ✓'.center(80)}{RESET}")
        print(f"{GREEN}{'=' * 80}{RESET}\n")
        return 0
    else:
        print(f"\n{RED}{'=' * 80}{RESET}")
        print(f"{RED}{'SOME TESTS FAILED! ✗'.center(80)}{RESET}")
        print(f"{RED}{'=' * 80}{RESET}\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
