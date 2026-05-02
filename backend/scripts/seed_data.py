"""
Seed initial data for development/testing
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.core.security import hash_password
from app.models.user import User, Permission, UserPermission, UserRole, UserStatus
from app.core.logging import logger


async def seed_data():
    """Seed initial data"""
    
    # Create async engine
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        try:
            # Create admin user
            admin_password = hash_password("admin123")
            admin = User(
                name="System Administrator",
                email="admin@itms.com",
                password_hash=admin_password,
                role=UserRole.ADMIN,
                status=UserStatus.ACTIVE
            )
            session.add(admin)
            
            # Create test jawan user
            jawan_password = hash_password("jawan123")
            jawan = User(
                name="Test Jawan",
                email="jawan@itms.com",
                password_hash=jawan_password,
                role=UserRole.JAWAN,
                status=UserStatus.ACTIVE
            )
            session.add(jawan)
            
            await session.commit()
            await session.refresh(admin)
            await session.refresh(jawan)
            
            logger.info("✅ Users created successfully")
            logger.info(f"   Admin: admin@itms.com / admin123")
            logger.info(f"   Jawan: jawan@itms.com / jawan123")
            
            # Grant all permissions to jawan for testing
            from sqlalchemy import select
            result = await session.execute(select(Permission))
            permissions = result.scalars().all()
            
            for permission in permissions:
                user_permission = UserPermission(
                    user_id=jawan.id,
                    permission_id=permission.id
                )
                session.add(user_permission)
            
            await session.commit()
            
            logger.info("✅ Permissions granted to test jawan")
            logger.info(f"   Granted {len(permissions)} permissions")
            
            print("\n" + "="*60)
            print("🎉 Database seeded successfully!")
            print("="*60)
            print("\n📝 Test Credentials:")
            print("-" * 60)
            print("Admin:")
            print("  Email:    admin@itms.com")
            print("  Password: admin123")
            print("\nJawan:")
            print("  Email:    jawan@itms.com")
            print("  Password: jawan123")
            print("="*60)
            
        except Exception as e:
            logger.error(f"❌ Error seeding data: {str(e)}")
            await session.rollback()
            raise
        finally:
            await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed_data())
