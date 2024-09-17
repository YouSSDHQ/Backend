import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

load_dotenv()
DATABASE_URL = (
    os.getenv("DATABASE_URL")
    if os.getenv("env") == "dev"
    else os.getenv("PG_DATABASE_URL")
)


def get_engine():
    return create_async_engine(DATABASE_URL, echo=True)


engine = get_engine()


@asynccontextmanager
async def get_session():
    async_session = async_sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()
            await engine.dispose()


# Database setup
async def init_db():
    async with engine.begin() as conn:
        # Import all models here
        from models.base import Base

        # Create tables
        await conn.run_sync(Base.metadata.create_all)
