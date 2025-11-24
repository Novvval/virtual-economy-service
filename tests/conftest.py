import asyncio

import pytest
from httpx import AsyncClient, ASGITransport

from src.presentation.api.main import app


pytestmark = pytest.mark.anyio

@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture()
def api_client():
    config = app.container.config
    config.set("active_test", True)
    config.set("redis_host", "localhost")
    config.set("database_url", "postgresql+asyncpg://postgres:postgres@localhost:5432/postgres")

    client = AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://localhost",
    )
    yield client
