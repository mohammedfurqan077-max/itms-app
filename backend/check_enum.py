"""Check junction status enum values in database"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.core.config import settings

async def check_enum():
    engine = create_async_engine(settings.DATABASE_URL)
    
    async with engine.connect() as conn:
        # Check enum values
        result = await conn.execute(text(
            "SELECT unnest(enum_range(NULL::junctionstatus))::text"
        ))
        values = [row[0] for row in result]
        
        print("Junction Status Enum Values in Database:")
        for val in values:
            print(f"  - {val}")
    
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(check_enum())
