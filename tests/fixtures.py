import pytest_asyncio
import httpx

from app.main import app  # inited FastAPI app


@pytest_asyncio.fixture
async def client():
    host, port = "127.0.0.1", "8080"
    async with httpx.AsyncClient(
        app=app, base_url=f"http://{host}:{port}", headers={"X-User-Fingerprint": "Test"}
    ) as client:
        yield client
