"""
Test script to verify ENUM removal is complete
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, text

from app.core.config import settings
from app.core.security import hash_password
from app.models.user import User, UserRole, UserStatus
from app.models.junction import Junction, JunctionStatus
from app.models.command import Command, CommandType, CommandStatus as CmdStatus


async def test_enum_removal():
    """Test that all ENUM types have been removed"""
    print("=" * 70)
    print("TESTING ENUM REMOVAL")
    print("=" * 70)
    
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    try:
        async with async_session() as session:
            # Test 1: Check for PostgreSQL ENUM types
            print("\n1. Checking for PostgreSQL ENUM types...")
            result = await session.execute(
                text("SELECT typname FROM pg_type WHERE typtype = 'e'")
            )
            enum_types = result.scalars().all()
            
            if enum_types:
                print(f"   ❌ FAILED: Found {len(enum_types)} ENUM types:")
                for enum_type in enum_types:
                    print(f"      - {enum_type}")
                return False
            else:
                print("   ✅ PASSED: No PostgreSQL ENUM types found")
            
            # Test 2: Verify User model uses STRING
            print("\n2. Testing User model with STRING fields...")
            test_user = User(
                email="test@example.com",
                password_hash=hash_password("test123"),
                name="Test User",
                role=UserRole.JAWAN,  # Should be string constant
                status=UserStatus.ACTIVE  # Should be string constant
            )
            session.add(test_user)
            await session.flush()
            
            # Verify the values are strings
            assert isinstance(test_user.role, str), "Role should be string"
            assert isinstance(test_user.status, str), "Status should be string"
            assert test_user.role == "jawan", f"Role should be 'jawan', got '{test_user.role}'"
            assert test_user.status == "active", f"Status should be 'active', got '{test_user.status}'"
            
            print(f"   ✅ PASSED: User created with role='{test_user.role}', status='{test_user.status}'")
            
            # Test 3: Verify Junction model uses STRING
            print("\n3. Testing Junction model with STRING fields...")
            test_junction = Junction(
                name="Test Junction",
                ip_address="192.168.1.200",
                device_id="TEST-001",
                status=JunctionStatus.OFFLINE,  # Should be string constant
                zone="Test Zone"
            )
            session.add(test_junction)
            await session.flush()
            
            # Verify the value is string
            assert isinstance(test_junction.status, str), "Status should be string"
            assert test_junction.status == "offline", f"Status should be 'offline', got '{test_junction.status}'"
            
            print(f"   ✅ PASSED: Junction created with status='{test_junction.status}'")
            
            # Test 4: Verify Command model uses STRING
            print("\n4. Testing Command model with STRING fields...")
            test_command = Command(
                junction_id=test_junction.id,
                command_type=CommandType.SET_MODE,  # Should be string constant
                status=CmdStatus.PENDING,  # Should be string constant
                payload='{"mode": "auto"}',
                created_by=test_user.id
            )
            session.add(test_command)
            await session.flush()
            
            # Verify the values are strings
            assert isinstance(test_command.command_type, str), "Command type should be string"
            assert isinstance(test_command.status, str), "Status should be string"
            assert test_command.command_type == "set_mode", f"Type should be 'set_mode', got '{test_command.command_type}'"
            assert test_command.status == "pending", f"Status should be 'pending', got '{test_command.status}'"
            
            print(f"   ✅ PASSED: Command created with type='{test_command.command_type}', status='{test_command.status}'")
            
            # Test 5: Verify database column types
            print("\n5. Checking database column types...")
            
            # Check users table
            result = await session.execute(
                text("""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name = 'users' 
                    AND column_name IN ('role', 'status')
                    ORDER BY column_name
                """)
            )
            user_columns = result.fetchall()
            
            for col_name, data_type in user_columns:
                if data_type not in ['character varying', 'varchar', 'text']:
                    print(f"   ❌ FAILED: users.{col_name} is {data_type}, should be VARCHAR")
                    return False
                print(f"   ✅ users.{col_name}: {data_type}")
            
            # Check junctions table
            result = await session.execute(
                text("""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name = 'junctions' 
                    AND column_name = 'status'
                """)
            )
            junction_columns = result.fetchall()
            
            for col_name, data_type in junction_columns:
                if data_type not in ['character varying', 'varchar', 'text']:
                    print(f"   ❌ FAILED: junctions.{col_name} is {data_type}, should be VARCHAR")
                    return False
                print(f"   ✅ junctions.{col_name}: {data_type}")
            
            # Check commands table
            result = await session.execute(
                text("""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name = 'commands' 
                    AND column_name IN ('command_type', 'status')
                    ORDER BY column_name
                """)
            )
            command_columns = result.fetchall()
            
            for col_name, data_type in command_columns:
                if data_type not in ['character varying', 'varchar', 'text']:
                    print(f"   ❌ FAILED: commands.{col_name} is {data_type}, should be VARCHAR")
                    return False
                print(f"   ✅ commands.{col_name}: {data_type}")
            
            # Rollback test data
            await session.rollback()
            
            print("\n" + "=" * 70)
            print("✅ ALL TESTS PASSED - ENUM REMOVAL COMPLETE")
            print("=" * 70)
            print("\nSummary:")
            print("  ✓ No PostgreSQL ENUM types in database")
            print("  ✓ User model uses STRING for role and status")
            print("  ✓ Junction model uses STRING for status")
            print("  ✓ Command model uses STRING for command_type and status")
            print("  ✓ All database columns are VARCHAR/TEXT")
            print("\n🚀 Backend is ready for Railway deployment!")
            
            return True
            
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        await engine.dispose()


if __name__ == "__main__":
    success = asyncio.run(test_enum_removal())
    sys.exit(0 if success else 1)
