import httpx
import pytest
import pytest_asyncio
from fastapi import FastAPI
from fastapi_users.db import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.main import app  # inited FastAPI app
from app.user.auth import UserManager, get_user_manager
from app.user.models import OAuthAccount, User
from app.user.schemas import UserCreate


@pytest.fixture(autouse=True)
def test_app() -> FastAPI:
    yield app


HOST, PORT = "127.0.0.1", "8080"


@pytest_asyncio.fixture
async def client(test_app: FastAPI) -> httpx.AsyncClient:
    host, port = HOST, PORT
    async with httpx.AsyncClient(
        app=app, base_url=f"http://{host}:{port}", headers={"X-User-Fingerprint": "Test"}
    ) as client:
        yield client


@pytest_asyncio.fixture
async def user_manager(async_session: AsyncSession) -> UserManager:
    user_db = SQLAlchemyUserDatabase(async_session, User, OAuthAccount)
    yield UserManager(user_db)


@pytest_asyncio.fixture
async def test_user(user_manager: UserManager) -> User:
    user = await user_manager.create(
        UserCreate(
            email="test@example.com",
            first_name="Momo",
            last_name="Test",
            locale="en_US",
            password="password",
            is_active=True,
            is_verified=True,
        )
    )
    yield user


@pytest_asyncio.fixture
async def test_superuser(user_manager: UserManager) -> User:
    user = await user_manager.create(
        UserCreate(
            email="super@example.com",
            first_name="Super",
            last_name="User",
            locale="en_US",
            password="password",
            is_active=True,
            is_verified=True,
            is_superuser=True,
        )
    )
    yield user


@pytest_asyncio.fixture
async def authenticated_client_user(client: httpx.AsyncClient, test_user: User) -> httpx.AsyncClient:
    data = {"username": test_user.email, "password": "password", "grant_type": "password"}
    response = await client.post("/users/auth/jwt/login", data=data)
    assert response.status_code == 200
    content = response.json()
    assert "access_token" in content
    token = content["access_token"]
    client.headers["Authorization"] = f"Bearer {token}"
    yield client


@pytest_asyncio.fixture
async def authenticated_client_superuser(client: httpx.AsyncClient, test_superuser: User) -> httpx.AsyncClient:
    data = {"username": test_superuser.email, "password": "password", "grant_type": "password"}
    response = await client.post("/users/auth/jwt/login", data=data)
    assert response.status_code == 200
    content = response.json()
    assert "access_token" in content
    token = content["access_token"]
    client.headers["Authorization"] = f"Bearer {token}"
    yield client
