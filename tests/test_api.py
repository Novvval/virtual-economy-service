from uuid import uuid4

import pytest
from httpx import AsyncClient

from src.infrastructure.utils.helpers import generate_jwt
from src.presentation.api.main import app


@pytest.fixture(scope="function")
def current_user_data():
    container = app.container
    id_payload = {"id": 1}
    jwt = generate_jwt(id_payload, container.config.secret_key())

    return {
        "user_id": 1,
        "product_id": 1,
        "headers": {
            "Authorization": f"Bearer {jwt}",
            "Idempotency-Key": str(uuid4())
        }
    }

class TestAPIIntegration:
    @pytest.mark.asyncio
    async def test_add_funds(self, api_client: AsyncClient, current_user_data):
        response = await api_client.post(
            f"/users/{current_user_data['user_id']}/add-funds",
            headers=current_user_data["headers"],
            json={"amount": 100},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == current_user_data["user_id"]
        assert data["message"] == "Funds added"
        assert "previous_balance" in data
        assert "current_balance" in data

    @pytest.mark.asyncio
    async def test_use_product(self, api_client: AsyncClient, current_user_data):
        response = await api_client.post(
            f"/products/{current_user_data['product_id']}/use",
            headers=current_user_data["headers"],
            json={"amount": 1},
        )
        data = response.json()
        assert response.status_code == 200
        assert data["message"] == "Product consumed"
        assert data["product_id"] == current_user_data["product_id"]
        assert "previous_quantity" in data
        assert "current_quantity" in data

    @pytest.mark.asyncio
    async def test_purchase_product(self, api_client: AsyncClient, current_user_data):
        response = await api_client.post(
            f"/products/{current_user_data['product_id']}/purchase",
            headers=current_user_data["headers"],
            json={"amount": 1},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Product purchased"
        assert data["product_id"] == current_user_data["product_id"]
        assert "price" in data
        assert "balance" in data


    @pytest.mark.asyncio
    async def test_analytics(self, api_client: AsyncClient):
        response = await api_client.get("/analytics/popular-products")
        assert response.status_code == 200
        assert response.json()["products"]

    @pytest.mark.asyncio
    async def test_show_inventory(self, api_client: AsyncClient, current_user_data):
        response = await api_client.get(
            f"/users/{current_user_data['user_id']}/inventory", headers=current_user_data["headers"],
        )
        assert response.status_code == 200
        assert response.json()["products"]