"""
Check database connection and users table
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, text

from app.core.config import settings
from app.models.user import User

async def check_database():
    print("Checking database connection...")
    print(f"Database URL: {settings.DATABASE_URL[:50]}...")
    print("-" * 50)
    
    try:
        engine = create_async_engine(settings.DATABASE_URL)
        async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        
        async with async_session() as session:
            # Test connection
            result = await session.execute(text("SELECT 1"))
            print("✅ Database connection successful!")
            
            # Check if users table exists
            result = await session.execute(
                text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'users')")
            )
            table_exists = result.scalar()
            
            if table_exists:
                print("✅ Users table exists")
                
                # Count users
                result = await session.execute(select(User))
                users = result.scalars().all()
                print(f"✅ Found {len(users)} user(s) in database")
                
                if users:
                    print("\nExisting users:")
                    for user in users:
                        print(f"  - {user.email} (ID: {user.id}, Active: {user.is_active}, Superuser: {user.is_superuser})")
                else:
                    print("\n⚠️  No users found in database")
                    print("   Run: python create_admin.py")
            else:
                print("❌ Users table does not exist")
                print("   Run migrations: alembic upgrade head")
        
        await engine.dispose()
        
    except Exception as e:
        print(f"❌ Database error: {str(e)}")
        print("\nPossible issues:")
        print("  1. Database URL is incorrect")
        print("  2. Database is not accessible")
        print("  3. Migrations not run")
        print("\nCheck your .env file and run: alembic upgrade head")

if __name__ == "__main__":
    asyncio.run(check_database())
