import httpx
import pytest

from fintables.api.endpoints.symbols import get_symbol_summary
from tests.conftest import load_fixture


@pytest.mark.asyncio
async def test_get_symbol_summary(create_mock_client):
    data = load_fixture("symbol_summary_asels.json")

    async def handler(request: httpx.Request) -> httpx.Response:
        assert "/mobile/symbols/ASELS/summary/" in str(request.url)
        return httpx.Response(200, json=data)

    client = create_mock_client(handler)
    summary = await get_symbol_summary(client, "ASELS")

    assert summary.data.multipliers.title == "Çarpanlar"
    assert len(summary.data.multipliers.data) == 3
    assert summary.data.multipliers.data[0].title == "F/K"
    assert summary.data.multipliers.data[0].value == "41.68"
    assert summary.data.yield_.title == "Getiri Analizi"
    assert "1w" in summary.data.yield_.data
    assert summary.data.yield_.data["1w"].high == 407.0
