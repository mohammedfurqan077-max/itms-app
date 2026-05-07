"""
Create admin user
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

from app.core.config import settings
from app.core.security import hash_password
from app.models.user import User

async def create_admin():
    engine = create_async_engine(settings.DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # Check if admin exists
        result = await session.execute(
            select(User).where(User.email == "admin@itms.com")
        )
        admin = result.scalar_one_or_none()
        
        if admin:
            print("ℹ️  Admin user already exists")
            print(f"   Email: {admin.email}")
            print(f"   Name: {admin.name}")
            print(f"   Role: {admin.role}")
            print(f"   Status: {admin.status}")
        else:
            # Create admin user
            from app.models.user import UserRole, UserStatus
            admin = User(
                email="admin@itms.com",
                password_hash=hash_password("admin123"),
                name="System Administrator",
                role=UserRole.ADMIN,
                status=UserStatus.ACTIVE
            )
            session.add(admin)
            await session.commit()
            await session.refresh(admin)
            
            print("✅ Admin user created successfully!")
            print(f"   Email: admin@itms.com")
            print(f"   Password: admin123")
            print(f"   ID: {admin.id}")
            print(f"   Role: {admin.role}")
            print(f"   Status: {admin.status}")
    
    await engine.dispose()

if __name__ == "__main__":
    print("Creating admin user...")
    print("-" * 50)
    asyncio.run(create_admin())
    print("-" * 50)
    print("\nYou can now login with:")
    print("  Email: admin@itms.com")
    print("  Password: admin123")
