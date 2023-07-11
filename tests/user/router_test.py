import httpx
import pytest
from firebase_admin import auth

from app.user.models import User
from tests.fixtures.core import exchange_custom_token_for_id_token


@pytest.mark.asyncio
async def test_create_user(client: httpx.AsyncClient, test_firebase_user: auth.UserRecord):
    custom_token = auth.create_custom_token(test_firebase_user.uid)
    id_token = await exchange_custom_token_for_id_token(custom_token.decode("utf-8"))
    response = await client.post(
        "/users",
        json={
            "email": test_firebase_user.email,
            "firebase_id_token": id_token,
            "first_name": "Test",
            "last_name": "User",
            "locale": "test",
        },
    )
    assert response.status_code == 200
    db_user = await User.get_by_firebase_uid(test_firebase_user.uid)
    assert db_user is not None
    assert response.json() == {
        "id": str(db_user.id),
        "email": db_user.email,
        "firebase_uid": db_user.firebase_uid,
        "first_name": db_user.first_name,
        "last_name": db_user.last_name,
        "locale": db_user.locale,
    }


@pytest.mark.asyncio
async def test_create_user_already_exists(client: httpx.AsyncClient, test_user: User):
    custom_token = auth.create_custom_token(test_user.firebase_uid)
    id_token = await exchange_custom_token_for_id_token(custom_token.decode("utf-8"))
    response = await client.post(
        "/users",
        json={
            "email": test_user.email,
            "firebase_id_token": id_token,
            "first_name": "Test",
            "last_name": "User",
            "locale": "test",
        },
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "User already registered"}


@pytest.mark.asyncio
async def test_create_user_invalid_token(client: httpx.AsyncClient):
    invalid_id_token = "invalid_id_token"
    response = await client.post(
        "/users",
        json={
            "email": "fake@email.com",
            "firebase_id_token": invalid_id_token,
            "first_name": "Test",
            "last_name": "User",
            "locale": "test",
        },
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_me(authenticated_client_user: httpx.AsyncClient, test_user: User):
    response = await authenticated_client_user.get("/users/me")
    assert response.status_code == 200
    assert response.json() == {
        "id": str(test_user.id),
        "email": test_user.email,
        "firebase_uid": test_user.firebase_uid,
        "first_name": test_user.first_name,
        "last_name": test_user.last_name,
        "locale": test_user.locale,
    }
