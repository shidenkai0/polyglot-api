from typing import AsyncGenerator

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.tutor.models import ModelName, Tutor


@pytest_asyncio.fixture
async def test_tutor(async_session: AsyncSession) -> AsyncGenerator[Tutor, None]:
    """Create a new Tutor object for testing."""
    tutor = Tutor(
        name="Tutor",
        avatar_url="https://cdn-icons-png.flaticon.com/512/168/168726.png",
        model=ModelName.GPT3_5_TURBO.value,
    )
    async_session.add(tutor)
    await async_session.commit()
    yield tutor
