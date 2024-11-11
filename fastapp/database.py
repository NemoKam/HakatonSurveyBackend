from typing import AsyncIterator

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, async_sessionmaker, AsyncSession

import config
from . import models

SQLALCHEMY_SYNC_DATABASE_URL = f"postgresql+psycopg2://{config.DATABASE_USER}:{config.DATABASE_PASSWORD}@{config.DATABASE_HOST}:{config.DATABASE_PORT}/{config.DATABASE_NAME}"
SQLALCHEMY_ASYNC_DATABASE_URL = f"postgresql+asyncpg://{config.DATABASE_USER}:{config.DATABASE_PASSWORD}@{config.DATABASE_HOST}:{config.DATABASE_PORT}/{config.DATABASE_NAME}"

class DatabaseSessionManager:
    def __init__(self):
        self.engine: AsyncEngine | None = None
        self.session_maker = None
        self.session = None

    def init_db(self, another_databse_uri: str | None = None):
        database_uri = SQLALCHEMY_ASYNC_DATABASE_URL
        if another_databse_uri:
            database_uri = another_databse_uri

        self.engine = create_async_engine(
            database_uri, pool_size=100, max_overflow=0, pool_pre_ping=False
        )
        self.sync_engine = create_engine(SQLALCHEMY_SYNC_DATABASE_URL)

        self.session_maker = async_sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )

    def create_tables(self):
        models.Base.metadata.create_all(bind=self.sync_engine)

    async def close(self):
        if self.engine is None:
            raise Exception("DatabaseSessionManager is not initialized")
        await self.engine.dispose()


sessionmanager = DatabaseSessionManager()
sessionmanager.init_db()


async def get_db() -> AsyncIterator[AsyncSession]:
    session = sessionmanager.session_maker()
    if session is None:
        raise Exception("DatabaseSessionManager is not initialized")
    try:
        yield session
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()
