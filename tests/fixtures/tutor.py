import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.tutor.models import ModelName, Tutor


@pytest_asyncio.fixture
async def test_tutor(async_session: AsyncSession) -> Tutor:
    """Create a new Tutor object for testing."""
    tutor = Tutor(name="Tutor", model=ModelName.GPT3_5_TURBO.value)
    async_session.add(tutor)
    await async_session.commit()
    yield tutor
