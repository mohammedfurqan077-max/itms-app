from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.user import User
from app.core.security import hash_password


async def create_user(db: AsyncSession, name: str, email: str, password: str):
    result = await db.execute(select(User).where(User.email == email))
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise Exception("User already exists")

    user = User(
        name=name,
        email=email,
        password_hash=hash_password(password),
        role="jawan"
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    return user