import pytest
from httpx import AsyncClient

from app.user.models import User


@pytest.mark.asyncio
async def test_user_me(authenticated_client: AsyncClient, test_user: User):
    response = await authenticated_client.get("/users/me")
    assert response.status_code == 200
    assert response.json() == {
        "id": str(test_user.id),
        "email": test_user.email,
        "is_active": test_user.is_active,
        "is_superuser": test_user.is_superuser,
        "is_verified": test_user.is_verified,
    }
