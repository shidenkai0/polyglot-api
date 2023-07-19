from typing import AsyncGenerator, Generator

import httpx
import pytest_asyncio
from fastapi import FastAPI
from firebase_admin import auth

from app.app import create_app
from app.config import settings
from app.user.auth import ActiveVerifiedUser, SuperUser
from app.user.models import User


@pytest_asyncio.fixture(autouse=True)
def test_app() -> Generator[FastAPI, None, None]:
    """
    Test the FastAPI app.
    """
    app = create_app()

    @app.get("/verifieduser")
    async def get_active_user(user: ActiveVerifiedUser):
        return {"id": user.id, "email": user.email}

    @app.get("/superuser")
    async def get_superuser(user: SuperUser):
        return {"id": user.id, "email": user.email}

    yield app


HOST, PORT = "127.0.0.1", "8080"


async def create_firebase_user(email: str, verified: bool) -> auth.UserRecord:
    """Creates a new Firebase user."""
    firebase_user = None
    try:
        firebase_user = auth.get_user_by_email(email)
    except auth.UserNotFoundError:
        firebase_user = auth.create_user(
            email=email,
            password='secretPassword',
            email_verified=verified,
        )
    yield firebase_user
    auth.delete_user(firebase_user.uid)


@pytest_asyncio.fixture
async def test_firebase_user() -> AsyncGenerator[auth.UserRecord, None]:
    """Test creating a new Firebase user."""
    user_email = "user@test.com"
    async for user in create_firebase_user(user_email, True):
        yield user


@pytest_asyncio.fixture
async def test_firebase_unverified_user() -> AsyncGenerator[auth.UserRecord, None]:
    """Test creating a new unverified Firebase user."""
    unverified_user_email = "unverified@test.com"
    async for user in create_firebase_user(unverified_user_email, False):
        yield user


@pytest_asyncio.fixture
async def test_firebase_superuser() -> AsyncGenerator[auth.UserRecord, None]:
    """Test creating a new superuser Firebase user."""
    superuser_email = "superuser@test.com"
    async for user in create_firebase_user(superuser_email, True):
        yield user


async def create_test_user(firebase_user: auth.UserRecord, is_superuser: bool) -> User:
    """Create a test User object in the database."""
    user = await User.create(
        email=firebase_user.email,
        firebase_uid=firebase_user.uid,
        name="First",
        locale="en_US",
        is_superuser=is_superuser,
    )
    assert user.id is not None
    return user


@pytest_asyncio.fixture
async def test_user(test_firebase_user: auth.UserRecord) -> AsyncGenerator[User, None]:
    """Test creating a new User object."""
    user = await create_test_user(test_firebase_user, False)
    yield user


@pytest_asyncio.fixture
async def test_unverified_user(test_firebase_unverified_user: auth.UserRecord) -> AsyncGenerator[User, None]:
    """Test creating a new unverified User object."""
    user = await create_test_user(test_firebase_unverified_user, False)
    yield user


@pytest_asyncio.fixture
async def test_superuser(test_firebase_superuser: auth.UserRecord) -> AsyncGenerator[User, None]:
    """Test creating a new superuser User object."""
    user = await create_test_user(test_firebase_superuser, True)
    yield user


@pytest_asyncio.fixture
async def client(test_app: FastAPI) -> AsyncGenerator[httpx.AsyncClient, None]:
    host, port = HOST, PORT
    async with httpx.AsyncClient(
        app=test_app, base_url=f"http://{host}:{port}", headers={"X-User-Fingerprint": "Test"}
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
async def authenticated_client_unverified_user(
    client: httpx.AsyncClient, test_unverified_user: User
) -> AsyncGenerator[httpx.AsyncClient, None]:
    custom_token = auth.create_custom_token(test_unverified_user.firebase_uid)
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
