import asyncio
import logging
from sqlalchemy import text
from app.db.session import engine
from app.models.base import Base
# Import all models to ensure they are registered with Base
from app.models import *

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def create_tables():
    logger.info("Creating tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Tables created successfully.")

if __name__ == "__main__":
    asyncio.run(create_tables())
