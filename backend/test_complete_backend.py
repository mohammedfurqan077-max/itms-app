"""
Complete Backend Test Suite
Tests database, tables, data storage, and all API endpoints
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, text, inspect
import httpx
from datetime import datetime

from app.core.config import settings
from app.models.user import User, UserRole, UserStatus
from app.models.junction import Junction, JunctionStatus
from app.models.command import Command, CommandType, CommandStatus as CmdStatus
from app.models.system_state import SystemState


# Test configuration
API_BASE_URL = "http://localhost:8000/api/v1"
TEST_EMAIL = "test_user@itms.com"
TEST_PASSWORD = "TestPass123!"


class BackendTester:
    def __init__(self):
        self.engine = None
        self.async_session = None
        self.token = None
        self.test_results = {
            "database": [],
            "tables": [],
            "data_storage": [],
            "api_endpoints": []
        }
        self.passed = 0
        self.failed = 0
    
    def log_test(self, category, test_name, passed, message=""):
        """Log test result"""
        status = "✅ PASS" if passed else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "message": message
        }
        self.test_results[category].append(result)
        
        if passed:
            self.passed += 1
            print(f"  {status}: {test_name}")
        else:
            self.failed += 1
            print(f"  {status}: {test_name}")
            if message:
                print(f"      Error: {message}")
    
    async def setup(self):
        """Setup database connection"""
        print("\n" + "="*70)
        print("BACKEND COMPREHENSIVE TEST SUITE")
        print("="*70)
        
        self.engine = create_async_engine(settings.DATABASE_URL, echo=False)
        self.async_session = sessionmaker(
            self.engine, 
            class_=AsyncSession, 
            expire_on_commit=False
        )
    
    async def test_database_connection(self):
        """Test 1: Database Connection"""
        print("\n1. Testing Database Connection...")
        
        try:
            async with self.engine.begin() as conn:
                result = await conn.execute(text("SELECT 1"))
                value = result.scalar()
                
                if value == 1:
                    self.log_test("database", "Database connection", True)
                else:
                    self.log_test("database", "Database connection", False, "Query returned unexpected value")
        except Exception as e:
            self.log_test("database", "Database connection", False, str(e))
    
    async def test_database_info(self):
        """Test 2: Database Information"""
        print("\n2. Testing Database Information...")
        
        try:
            async with self.engine.begin() as conn:
                # Get database name
                result = await conn.execute(text("SELECT current_database()"))
                db_name = result.scalar()
                self.log_test("database", f"Database name: {db_name}", True)
                
                # Get PostgreSQL version
                result = await conn.execute(text("SELECT version()"))
                version = result.scalar()
                pg_version = version.split()[1] if version else "Unknown"
                self.log_test("database", f"PostgreSQL version: {pg_version}", True)
                
                # Check for ENUM types (should be none)
                result = await conn.execute(
                    text("SELECT typname FROM pg_type WHERE typtype = 'e'")
                )
                enum_types = result.scalars().all()
                
                if len(enum_types) == 0:
                    self.log_test("database", "No ENUM types (Railway compatible)", True)
                else:
                    self.log_test("database", "No ENUM types", False, 
                                f"Found {len(enum_types)} ENUM types: {enum_types}")
        except Exception as e:
            self.log_test("database", "Database information", False, str(e))
    
    async def test_tables_exist(self):
        """Test 3: Check All Tables Exist"""
        print("\n3. Testing Table Existence...")
        
        expected_tables = [
            'users',
            'permissions',
            'user_permissions',
            'sessions',
            'junctions',
            'commands',
            'system_state',
            'alembic_version'
        ]
        
        try:
            async with self.engine.begin() as conn:
                result = await conn.execute(
                    text("""
                        SELECT tablename 
                        FROM pg_tables 
                        WHERE schemaname = 'public'
                    """)
                )
                existing_tables = [row[0] for row in result.fetchall()]
                
                for table in expected_tables:
                    if table in existing_tables:
                        self.log_test("tables", f"Table '{table}' exists", True)
                    else:
                        self.log_test("tables", f"Table '{table}' exists", False, 
                                    "Table not found")
        except Exception as e:
            self.log_test("tables", "Check tables", False, str(e))
    
    async def test_table_structures(self):
        """Test 4: Verify Table Structures"""
        print("\n4. Testing Table Structures...")
        
        try:
            async with self.engine.begin() as conn:
                # Test users table
                result = await conn.execute(
                    text("""
                        SELECT column_name, data_type 
                        FROM information_schema.columns 
                        WHERE table_name = 'users'
                        ORDER BY ordinal_position
                    """)
                )
                user_columns = {row[0]: row[1] for row in result.fetchall()}
                
                required_user_columns = ['id', 'email', 'password_hash', 'role', 'status']
                for col in required_user_columns:
                    if col in user_columns:
                        self.log_test("tables", f"users.{col} column exists", True)
                    else:
                        self.log_test("tables", f"users.{col} column exists", False)
                
                # Verify role and status are VARCHAR (not ENUM)
                if user_columns.get('role') == 'character varying':
                    self.log_test("tables", "users.role is VARCHAR (not ENUM)", True)
                else:
                    self.log_test("tables", "users.role is VARCHAR", False, 
                                f"Type is {user_columns.get('role')}")
                
                if user_columns.get('status') == 'character varying':
                    self.log_test("tables", "users.status is VARCHAR (not ENUM)", True)
                else:
                    self.log_test("tables", "users.status is VARCHAR", False,
                                f"Type is {user_columns.get('status')}")
                
                # Test junctions table
                result = await conn.execute(
                    text("""
                        SELECT column_name, data_type 
                        FROM information_schema.columns 
                        WHERE table_name = 'junctions'
                    """)
                )
                junction_columns = {row[0]: row[1] for row in result.fetchall()}
                
                if 'status' in junction_columns:
                    if junction_columns['status'] == 'character varying':
                        self.log_test("tables", "junctions.status is VARCHAR (not ENUM)", True)
                    else:
                        self.log_test("tables", "junctions.status is VARCHAR", False,
                                    f"Type is {junction_columns['status']}")
                
                # Test commands table
                result = await conn.execute(
                    text("""
                        SELECT column_name, data_type 
                        FROM information_schema.columns 
                        WHERE table_name = 'commands'
                    """)
                )
                command_columns = {row[0]: row[1] for row in result.fetchall()}
                
                if 'command_type' in command_columns and 'status' in command_columns:
                    if command_columns['command_type'] == 'character varying':
                        self.log_test("tables", "commands.command_type is VARCHAR", True)
                    else:
                        self.log_test("tables", "commands.command_type is VARCHAR", False)
                    
                    if command_columns['status'] == 'character varying':
                        self.log_test("tables", "commands.status is VARCHAR", True)
                    else:
                        self.log_test("tables", "commands.status is VARCHAR", False)
        except Exception as e:
            self.log_test("tables", "Table structures", False, str(e))
    
    async def test_data_storage(self):
        """Test 5: Test Data Storage"""
        print("\n5. Testing Data Storage...")
        
        try:
            async with self.async_session() as session:
                # Test User creation
                test_user = User(
                    email=f"storage_test_{datetime.now().timestamp()}@test.com",
                    password_hash="test_hash",
                    name="Storage Test User",
                    role=UserRole.JAWAN,
                    status=UserStatus.ACTIVE
                )
                session.add(test_user)
                await session.flush()
                
                if test_user.id:
                    self.log_test("data_storage", "User creation", True, 
                                f"Created user with ID: {test_user.id}")
                else:
                    self.log_test("data_storage", "User creation", False, "No ID assigned")
                
                # Verify user data
                result = await session.execute(
                    select(User).where(User.id == test_user.id)
                )
                retrieved_user = result.scalar_one_or_none()
                
                if retrieved_user:
                    self.log_test("data_storage", "User retrieval", True)
                    
                    if retrieved_user.role == UserRole.JAWAN:
                        self.log_test("data_storage", "User role stored correctly", True)
                    else:
                        self.log_test("data_storage", "User role stored correctly", False,
                                    f"Expected 'jawan', got '{retrieved_user.role}'")
                else:
                    self.log_test("data_storage", "User retrieval", False)
                
                # Test Junction creation
                test_junction = Junction(
                    name=f"Test Junction {datetime.now().timestamp()}",
                    ip_address=f"192.168.1.{int(datetime.now().timestamp()) % 255}",
                    status=JunctionStatus.OFFLINE,
                    zone="Test Zone"
                )
                session.add(test_junction)
                await session.flush()
                
                if test_junction.id:
                    self.log_test("data_storage", "Junction creation", True,
                                f"Created junction with ID: {test_junction.id}")
                else:
                    self.log_test("data_storage", "Junction creation", False)
                
                # Test Command creation
                test_command = Command(
                    junction_id=test_junction.id,
                    command_type=CommandType.SET_MODE,
                    status=CmdStatus.PENDING,
                    payload='{"mode": "auto"}',
                    created_by=test_user.id
                )
                session.add(test_command)
                await session.flush()
                
                if test_command.id:
                    self.log_test("data_storage", "Command creation", True,
                                f"Created command with ID: {test_command.id}")
                    
                    if test_command.status == CmdStatus.PENDING:
                        self.log_test("data_storage", "Command status stored correctly", True)
                    else:
                        self.log_test("data_storage", "Command status stored correctly", False)
                else:
                    self.log_test("data_storage", "Command creation", False)
                
                # Test SystemState
                result = await session.execute(select(SystemState))
                system_state = result.scalar_one_or_none()
                
                if system_state:
                    self.log_test("data_storage", "SystemState exists", True)
                else:
                    self.log_test("data_storage", "SystemState exists", False,
                                "SystemState not initialized")
                
                # Rollback test data
                await session.rollback()
                self.log_test("data_storage", "Transaction rollback", True)
                
        except Exception as e:
            self.log_test("data_storage", "Data storage", False, str(e))
    
    async def test_api_endpoints(self):
        """Test 6: Test API Endpoints"""
        print("\n6. Testing API Endpoints...")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Test health endpoint
            try:
                response = await client.get(f"{API_BASE_URL.replace('/api/v1', '')}/health")
                if response.status_code == 200:
                    data = response.json()
                    if data.get("status") == "healthy":
                        self.log_test("api_endpoints", "GET /health", True)
                    else:
                        self.log_test("api_endpoints", "GET /health", False, 
                                    f"Status: {data.get('status')}")
                else:
                    self.log_test("api_endpoints", "GET /health", False,
                                f"Status code: {response.status_code}")
            except Exception as e:
                self.log_test("api_endpoints", "GET /health", False, str(e))
            
            # Test login endpoint
            try:
                response = await client.post(
                    f"{API_BASE_URL}/auth/login",
                    json={"email": "admin@itms.com", "password": "admin123"}
                )
                if response.status_code == 200:
                    data = response.json()
                    if "access_token" in data or "tokens" in data:
                        self.token = data.get("access_token") or data.get("tokens", {}).get("access_token")
                        self.log_test("api_endpoints", "POST /auth/login", True)
                    else:
                        self.log_test("api_endpoints", "POST /auth/login", False,
                                    "No access token in response")
                else:
                    self.log_test("api_endpoints", "POST /auth/login", False,
                                f"Status code: {response.status_code}")
            except Exception as e:
                self.log_test("api_endpoints", "POST /auth/login", False, str(e))
            
            if not self.token:
                print("  ⚠️  Cannot test authenticated endpoints without token")
                return
            
            headers = {"Authorization": f"Bearer {self.token}"}
            
            # Test junctions endpoints
            try:
                response = await client.get(f"{API_BASE_URL}/junctions", headers=headers)
                if response.status_code == 200:
                    self.log_test("api_endpoints", "GET /junctions", True)
                else:
                    self.log_test("api_endpoints", "GET /junctions", False,
                                f"Status code: {response.status_code}")
            except Exception as e:
                self.log_test("api_endpoints", "GET /junctions", False, str(e))
            
            # Test system state endpoint
            try:
                response = await client.get(f"{API_BASE_URL}/system/state", headers=headers)
                if response.status_code == 200:
                    self.log_test("api_endpoints", "GET /system/state", True)
                else:
                    self.log_test("api_endpoints", "GET /system/state", False,
                                f"Status code: {response.status_code}")
            except Exception as e:
                self.log_test("api_endpoints", "GET /system/state", False, str(e))
            
            # Test commands endpoint
            try:
                response = await client.get(f"{API_BASE_URL}/commands", headers=headers)
                if response.status_code == 200:
                    self.log_test("api_endpoints", "GET /commands", True)
                else:
                    self.log_test("api_endpoints", "GET /commands", False,
                                f"Status code: {response.status_code}")
            except Exception as e:
                self.log_test("api_endpoints", "GET /commands", False, str(e))
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.engine:
            await self.engine.dispose()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*70)
        print("TEST SUMMARY")
        print("="*70)
        
        total = self.passed + self.failed
        percentage = (self.passed / total * 100) if total > 0 else 0
        
        print(f"\nTotal Tests: {total}")
        print(f"Passed: {self.passed} ✅")
        print(f"Failed: {self.failed} ❌")
        print(f"Success Rate: {percentage:.1f}%")
        
        if self.failed > 0:
            print("\n" + "="*70)
            print("FAILED TESTS:")
            print("="*70)
            for category, results in self.test_results.items():
                failed_tests = [r for r in results if "❌" in r["status"]]
                if failed_tests:
                    print(f"\n{category.upper()}:")
                    for test in failed_tests:
                        print(f"  ❌ {test['test']}")
                        if test['message']:
                            print(f"     {test['message']}")
        
        print("\n" + "="*70)
        if self.failed == 0:
            print("✅ ALL TESTS PASSED - BACKEND IS PERFECT!")
        else:
            print(f"⚠️  {self.failed} TEST(S) FAILED - NEEDS ATTENTION")
        print("="*70)
    
    async def run_all_tests(self):
        """Run all tests"""
        await self.setup()
        await self.test_database_connection()
        await self.test_database_info()
        await self.test_tables_exist()
        await self.test_table_structures()
        await self.test_data_storage()
        await self.test_api_endpoints()
        await self.cleanup()
        self.print_summary()
        
        return self.failed == 0


async def main():
    """Main test function"""
    tester = BackendTester()
    success = await tester.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
