import httpx
import pytest

from app.tutor.models import Tutor
from app.tutor.router import TUTOR_NOT_FOUND
from app.tutor.schemas import PublicModelName, internal_to_public_model_name


@pytest.mark.asyncio
async def test_create_tutor(authenticated_client_superuser: httpx.AsyncClient):
    """Test creating a new tutor."""
    new_tutor = {"name": "TutorName", "language": "English", "visible": True, "model": PublicModelName.GPT3_5_TURBO}
    response = await authenticated_client_superuser.post("/tutor", json=new_tutor)
    assert response.status_code == 200
    assert response.json().keys() == {"id", "name", "visible", "language", "model"}
    assert response.json()["name"] == new_tutor["name"]
    assert response.json()["language"] == new_tutor["language"]
    assert response.json()["visible"] == new_tutor["visible"]
    assert response.json()["model"] == new_tutor["model"]


@pytest.mark.asyncio
async def test_create_tutor_as_user(authenticated_client_user: httpx.AsyncClient):
    """Test creating a new tutor as a user."""
    new_tutor = {"name": "TutorName", "language": "English", "visible": True, "model": PublicModelName.GPT3_5_TURBO}
    response = await authenticated_client_user.post("/tutor", json=new_tutor)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_get_tutor(test_tutor: Tutor, authenticated_client_superuser: httpx.AsyncClient):
    """Test getting a tutor by ID."""
    response = await authenticated_client_superuser.get(f"/tutor/{test_tutor.id}")
    assert response.status_code == 200
    assert response.json() == {
        "id": str(test_tutor.id),
        "name": test_tutor.name,
        "visible": test_tutor.visible,
        "language": test_tutor.language,
        "model": internal_to_public_model_name(test_tutor.model),
    }


@pytest.mark.asyncio
async def test_get_tutors_as_superuser(authenticated_client_superuser: httpx.AsyncClient):
    """Test getting all tutors as a superuser."""
    response = await authenticated_client_superuser.get("/tutors")
    assert response.status_code == 200
    assert response.json() == [
        {
            "id": str(tutor.id),
            "name": tutor.name,
            "visible": tutor.visible,
            "language": tutor.language,
            "model": tutor.model,
        }
        for tutor in await Tutor.get_all()
    ]


@pytest.mark.asyncio
async def test_get_tutors_as_user(authenticated_client_user: httpx.AsyncClient):
    """Test getting all tutors as a user."""
    response = await authenticated_client_user.get("/tutors")
    assert response.status_code == 200
    assert response.json() == [
        {
            "id": str(tutor.id),
            "name": tutor.name,
            "visible": tutor.visible,
            "language": tutor.language,
            "model": tutor.model,
        }
        for tutor in await Tutor.get_visible()
    ]


@pytest.mark.asyncio
async def test_get_tutor_not_found(authenticated_client_superuser: httpx.AsyncClient):
    """Test getting a tutor that does not exist."""
    response = await authenticated_client_superuser.get("/tutor/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404
    assert response.json() == {"detail": TUTOR_NOT_FOUND.detail}


@pytest.mark.asyncio
async def test_update_tutor(test_tutor: Tutor, authenticated_client_superuser: httpx.AsyncClient):
    """Test updating a tutor."""
    updated_tutor = {"name": "UpdatedName", "language": "UpdatedLanguage", "visible": False}
    response = await authenticated_client_superuser.put(f"/tutor/{test_tutor.id}", json=updated_tutor)
    assert response.status_code == 200
    assert response.json()["name"] == updated_tutor["name"]
    assert response.json()["language"] == updated_tutor["language"]
    assert response.json()["visible"] == updated_tutor["visible"]


@pytest.mark.asyncio
async def test_update_tutor_as_user(test_tutor: Tutor, authenticated_client_user: httpx.AsyncClient):
    """Test updating a tutor as a user."""
    updated_tutor = {"name": "UpdatedName", "language": "UpdatedLanguage", "visible": False}
    response = await authenticated_client_user.put(f"/tutor/{test_tutor.id}", json=updated_tutor)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_delete_tutor(test_tutor: Tutor, authenticated_client_superuser: httpx.AsyncClient):
    """Test deleting a tutor."""
    response = await authenticated_client_superuser.delete(f"/tutor/{test_tutor.id}")
    assert response.status_code == 204
    tutor = await Tutor.get(test_tutor.id)
    assert tutor is None


@pytest.mark.asyncio
async def test_delete_tutor_not_found(authenticated_client_superuser: httpx.AsyncClient):
    """Test deleting a tutor that does not exist."""
    response = await authenticated_client_superuser.delete("/tutor/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404
    assert response.json() == {"detail": TUTOR_NOT_FOUND.detail}
