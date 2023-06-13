import pytest

from .fixtures import client

from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health(client: AsyncClient):
    response = await client.get("/_health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
