import pytest


@pytest.mark.asyncio
async def test_authenticate_user(authenticated_client_user, test_user):
    response = await authenticated_client_user.get("/verifieduser")
    assert response.status_code == 200
    assert response.json() == {"id": str(test_user.id), "email": test_user.email}


@pytest.mark.asyncio
async def test_authenticate_unverified_user(authenticated_client_unverified_user):
    response = await authenticated_client_unverified_user.get("/verifieduser")
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_authenticate_superuser(authenticated_client_superuser, test_superuser):
    response = await authenticated_client_superuser.get("/superuser")
    assert response.status_code == 200
    assert response.json() == {"id": str(test_superuser.id), "email": test_superuser.email}


@pytest.mark.asyncio
async def test_authenticate_superuser_unauthorized(authenticated_client_user):
    response = await authenticated_client_user.get("/superuser")
    assert response.status_code == 403
