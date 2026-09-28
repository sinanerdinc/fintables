import httpx
import pytest

from fintables.api.endpoints.sheets import get_sheets
from tests.conftest import load_fixture


@pytest.mark.asyncio
async def test_get_sheets(create_mock_client):
    data = load_fixture("sheets_froto.json")
    captured_request = None

    async def handler(request: httpx.Request) -> httpx.Response:
        nonlocal captured_request
        captured_request = request
        return httpx.Response(200, json=data)

    client = create_mock_client(handler)
    sheets = await get_sheets(client, "froto")

    assert "/mobile/symbols/FROTO/sheets/" in str(captured_request.url)
    assert captured_request.headers["Authorization"] == "Bearer test_access_token"

    assert len(sheets.balance.periods) == 2
    assert sheets.balance.periods[0].year == 2026
    assert sheets.balance.periods[0].month == 6
    assert len(sheets.balance.rows) == 2
    assert sheets.balance.rows[0].label == "Dönen Varlıklar"
    assert sheets.balance.rows[0].level == 0
    assert sheets.balance.rows[1].label == "Nakit ve Nakit Benzerleri"
    assert sheets.balance.rows[1].level is None
    assert sheets.balance.rows[0].values[0] == 238889000000.0

    assert len(sheets.income.rows) == 1
    assert len(sheets.cashflow.rows) == 1
