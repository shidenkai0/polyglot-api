from uuid import UUID

import pytest

from app.tutor.models import ModelName, Tutor


@pytest.mark.asyncio
async def test_tutor_create():
    """Test creating a new Tutor object."""
    tutor = await Tutor.create(
        name="The E",
        avatar_url="https://cdn-icons-png.flaticon.com/512/168/168726.png",
        language="English",
        visible=True,
        model=ModelName.GPT3_5_TURBO,
    )
    assert tutor.id is not None


@pytest.mark.asyncio
async def test_tutor_get(test_tutor):
    """Test getting a Tutor object."""
    tutor = await Tutor.get(test_tutor.id)
    assert tutor is not None


@pytest.mark.asyncio
async def test_tutor_delete(test_tutor):
    """Test deleting a Tutor object."""
    await Tutor.delete(test_tutor.id)
    tutor = await Tutor.get(test_tutor.id)
    assert tutor is None


@pytest.mark.asyncio
async def test_tutor_get_not_found():
    """Test getting a Tutor object that does not exist."""
    tutor = await Tutor.get(UUID(int=0))
    assert tutor is None


@pytest.mark.asyncio
async def test_tutor_get_visible(test_tutor):
    """Test getting visible Tutor objects."""
    await Tutor.create(
        name="The Hidden E",
        avatar_url="https://cdn-icons-png.flaticon.com/512/168/168726.png",
        language="English",
        visible=False,
        model=ModelName.GPT3_5_TURBO,
    )
    tutors = await Tutor.get_visible()
    assert len(tutors) == 1
    assert tutors[0].id == test_tutor.id
