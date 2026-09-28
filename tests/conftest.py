import json
from pathlib import Path
from typing import Any
import httpx
import pytest

from fintables.api.client import FintablesClient
from fintables.config import Settings

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def load_fixture(filename: str) -> dict[str, Any]:
    with open(FIXTURES_DIR / filename, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture
def mock_settings() -> Settings:
    return Settings(
        base_url="https://api.fintables.com",
        gate_url="https://gate.fintables.com",
        mobile_build=323,
        mobile_version="2.28.2",
        username="testuser",
        password="testpassword",
    )


class MockTransport(httpx.AsyncBaseTransport):
    def __init__(self, handler):
        self.handler = handler

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        return await self.handler(request)


@pytest.fixture
def create_mock_client(mock_settings):
    def _maker(handler):
        transport = MockTransport(handler)
        async_http_client = httpx.AsyncClient(transport=transport)
        return FintablesClient(
            custom_settings=mock_settings,
            access_token="test_access_token",
            refresh_token_val="test_refresh_token",
            client=async_http_client,
        )

    return _maker
