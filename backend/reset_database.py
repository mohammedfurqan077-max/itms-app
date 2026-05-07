"""
Reset database - Drop all tables and ENUM types, then run migrations fresh
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

from app.core.config import settings


async def reset_database():
    """Reset database by dropping all tables and ENUM types"""
    print("=" * 70)
    print("RESETTING DATABASE")
    print("=" * 70)
    print(f"\nDatabase: {settings.DATABASE_URL.split('@')[1] if '@' in settings.DATABASE_URL else 'hidden'}")
    print("\n⚠️  WARNING: This will delete ALL data in the database!")
    
    response = input("\nAre you sure you want to continue? (yes/no): ")
    if response.lower() != "yes":
        print("❌ Aborted")
        return False
    
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    
    try:
        async with engine.begin() as conn:
            print("\n1. Dropping all tables...")
            
            # Drop tables in correct order (respecting foreign keys)
            tables = [
                'commands',
                'system_state',
                'sessions',
                'user_permissions',
                'permissions',
                'junctions',
                'users',
                'alembic_version'
            ]
            
            for table in tables:
                try:
                    await conn.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE"))
                    print(f"   ✓ Dropped table: {table}")
                except Exception as e:
                    print(f"   ⚠ Could not drop {table}: {e}")
            
            print("\n2. Dropping all ENUM types...")
            
            # Drop all ENUM types
            enum_types = [
                'commandstatus',
                'commandtype',
                'junctionstatus',
                'userstatus',
                'userrole'
            ]
            
            for enum_type in enum_types:
                try:
                    await conn.execute(text(f"DROP TYPE IF EXISTS {enum_type} CASCADE"))
                    print(f"   ✓ Dropped ENUM type: {enum_type}")
                except Exception as e:
                    print(f"   ⚠ Could not drop {enum_type}: {e}")
            
            print("\n3. Verifying cleanup...")
            
            # Check for remaining ENUM types
            result = await conn.execute(
                text("SELECT typname FROM pg_type WHERE typtype = 'e'")
            )
            remaining_enums = result.scalars().all()
            
            if remaining_enums:
                print(f"   ⚠ Warning: {len(remaining_enums)} ENUM types still exist:")
                for enum_type in remaining_enums:
                    print(f"      - {enum_type}")
            else:
                print("   ✅ All ENUM types removed")
            
            # Check for remaining tables
            result = await conn.execute(
                text("""
                    SELECT tablename 
                    FROM pg_tables 
                    WHERE schemaname = 'public'
                    AND tablename NOT LIKE 'pg_%'
                    AND tablename NOT LIKE 'sql_%'
                """)
            )
            remaining_tables = result.scalars().all()
            
            if remaining_tables:
                print(f"   ℹ️  {len(remaining_tables)} tables still exist:")
                for table in remaining_tables:
                    print(f"      - {table}")
            else:
                print("   ✅ All tables removed")
        
        print("\n" + "=" * 70)
        print("✅ DATABASE RESET COMPLETE")
        print("=" * 70)
        print("\nNext steps:")
        print("  1. Run migrations: alembic upgrade head")
        print("  2. Create admin user: python create_admin.py")
        print("  3. Test enum removal: python test_enum_removal.py")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        await engine.dispose()


if __name__ == "__main__":
    success = asyncio.run(reset_database())
    sys.exit(0 if success else 1)
