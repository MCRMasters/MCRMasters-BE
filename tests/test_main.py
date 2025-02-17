import pytest
from fastapi import status


@pytest.mark.asyncio
async def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["status"] == "healthy"
