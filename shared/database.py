from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from sqlmodel import SQLModel
import os
import logging

logger = logging.getLogger(__name__)

# Create async engine for Aiven PostgreSQL
engine = create_async_engine(
    os.getenv("DATABASE_URL"),
    echo=False,
    future=True,
    poolclass=NullPool,
    connect_args={
        "ssl": "require"
    } if "ssl=require" in os.getenv("DATABASE_URL", "") else {}
)

# Create async session factory
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_session() -> AsyncSession:
    """Dependency for getting async database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def create_db_and_tables():
    """Create all database tables"""
    logger.info("🗄️ Creating database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    logger.info("✅ Database tables created successfully!")
