from fastapi import status
from httpx import AsyncClient


async def test_health_check(client: AsyncClient):
    response = await client.get("/health")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "healthy"
