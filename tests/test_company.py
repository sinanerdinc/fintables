import httpx
import pytest

from fintables.api.endpoints.companies import get_company
from tests.conftest import load_fixture


@pytest.mark.asyncio
async def test_get_company(create_mock_client):
    data = load_fixture("company_asels.json")

    async def handler(request: httpx.Request) -> httpx.Response:
        assert "/companies/ASELS/" in str(request.url)
        return httpx.Response(200, json=data)

    client = create_mock_client(handler)
    company = await get_company(client, "asels")

    assert company.code == "ASELS"
    assert company.price == 377.0
    assert company.enflasyon is True
    assert company.in_katilim_index is True
    assert len(company.ratio_types) == 2
    assert company.ratio_types[0].name == "Likidite Oranları"
    assert company.ratio_types[0].data[0].allowed is True
