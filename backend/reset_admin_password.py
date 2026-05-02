"""
Reset admin password to admin123
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

async def reset_password():
    engine = create_async_engine(settings.DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # Get admin user
        result = await session.execute(
            select(User).where(User.email == "admin@itms.com")
        )
        admin = result.scalar_one_or_none()
        
        if admin:
            # Reset password
            admin.password_hash = hash_password("admin123")
            await session.commit()
            print("✅ Admin password reset to: admin123")
        else:
            print("❌ Admin user not found")
    
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(reset_password())
