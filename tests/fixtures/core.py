from typing import AsyncGenerator, Generator

import httpx
import pytest_asyncio
from fastapi import FastAPI
from firebase_admin import auth

from app.config import settings
from app.main import app  # inited FastAPI app
from app.user.models import User


@pytest_asyncio.fixture(autouse=True)
def test_app() -> Generator[FastAPI, None, None]:
    """
    Test the FastAPI app.
    """
    yield app


HOST, PORT = "127.0.0.1", "8080"


@pytest_asyncio.fixture
async def test_user() -> AsyncGenerator[User, None]:
    """Test creating a new User object."""
    firebase_user = None
    try:
        firebase_user = auth.get_user_by_email('user@test.com')
    except auth.UserNotFoundError:
        firebase_user = auth.create_user(
            email='user@test.com',
            password='secretPassword',
        )
    user = await User.create(
        email="user@test.com",
        firebase_uid=firebase_user.uid,
        first_name="First",
        last_name="Last",
        locale="en_US",
        is_superuser=False,
    )
    assert user.id is not None
    yield user


@pytest_asyncio.fixture
async def test_superuser() -> AsyncGenerator[User, None]:
    """Test creating a new User object."""
    firebase_user = None
    try:
        firebase_user = auth.get_user_by_email('superuser@test.com')
    except auth.UserNotFoundError:
        firebase_user = auth.create_user(
            email='superuser@test.com',
            password='secretPassword',
        )
    user = await User.create(
        email="superuser@test.com",
        firebase_uid=firebase_user.uid,
        first_name="First",
        last_name="Last",
        locale="en_US",
        is_superuser=True,
    )
    assert user.id is not None
    yield user


@pytest_asyncio.fixture
async def client(test_app: FastAPI) -> AsyncGenerator[httpx.AsyncClient, None]:
    host, port = HOST, PORT
    async with httpx.AsyncClient(
        app=app, base_url=f"http://{host}:{port}", headers={"X-User-Fingerprint": "Test"}
    ) as client:
        yield client


async def exchange_custom_token_for_id_token(custom_token: str) -> str:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"http://{settings.FIREBASE_AUTH_EMULATOR_HOST}/identitytoolkit.googleapis.com/v1/accounts:signInWithCustomToken?key=API_KEY",
            json={'token': custom_token, 'returnSecureToken': True},
        )
        response.raise_for_status()

    data = response.json()
    return data['idToken']


@pytest_asyncio.fixture
async def authenticated_client_user(
    client: httpx.AsyncClient, test_user: User
) -> AsyncGenerator[httpx.AsyncClient, None]:
    custom_token = auth.create_custom_token(test_user.firebase_uid)
    id_token = await exchange_custom_token_for_id_token(custom_token.decode('utf-8'))
    client.headers["Authorization"] = f"Bearer {id_token}"
    yield client


@pytest_asyncio.fixture
async def authenticated_client_superuser(
    client: httpx.AsyncClient, test_superuser: User
) -> AsyncGenerator[httpx.AsyncClient, None]:
    custom_token = auth.create_custom_token(test_superuser.firebase_uid)
    id_token = await exchange_custom_token_for_id_token(custom_token.decode('utf-8'))
    client.headers["Authorization"] = f"Bearer {id_token}"
    yield client
