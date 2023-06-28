import uuid
from typing import AsyncGenerator
from unittest import mock

import asyncpg
import pytest
import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.engine.url import make_url
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config import settings


@pytest_asyncio.fixture
async def db_template() -> AsyncGenerator[str, None]:
    """
    Create a new database from the source database template and yield the temporary database URL.

    During teardown, the temporary database is deleted.

    Yields:
        str: The DSN for the temporary database.
    """
    # Connect to the source database
    source_db_url = make_url(settings.DATABASE_URL)
    source_db_name = source_db_url.database
    source_db_url_no_asyncpg = source_db_url.set(
        drivername="postgresql"
    )  # We are using asyncpg directly, so we need to change the drivername
    conn = await asyncpg.connect(source_db_url_no_asyncpg.render_as_string(hide_password=False))

    # Create a new database from template0
    db_name = f"test_db_{uuid.uuid4().hex}"
    await conn.execute(f"CREATE DATABASE {db_name} TEMPLATE {source_db_name}")
    await conn.close()

    temp_db_url = source_db_url.set(database=db_name).render_as_string(hide_password=False)
    yield temp_db_url

    # Delete the database
    conn = await asyncpg.connect(source_db_url_no_asyncpg.render_as_string(hide_password=False))
    await conn.execute(f"DROP DATABASE {db_name}")
    await conn.close()


@pytest_asyncio.fixture
async def async_engine(db_template: str) -> AsyncGenerator[AsyncEngine, None]:
    """Create a new SQLAlchemy async engine connected to the temporary database."""

    engine = create_async_engine(db_template, pool_size=settings.POOL_SIZE, max_overflow=settings.MAX_OVERFLOW)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def async_session(async_engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    """Create a new SQLAlchemy async session."""
    async_session = async_sessionmaker(async_engine, autocommit=False, autoflush=False, expire_on_commit=False)
    async with async_session() as session:
        yield session


@pytest.fixture(autouse=True)
def _patch_async_session(async_session: AsyncSession):
    """Patch app. to return the async_session fixture"""
    with mock.patch("app.database._async_session", lambda: async_session):
        yield
