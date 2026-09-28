import json
import httpx
import pytest

from fintables.api.endpoints.search import search
from tests.conftest import load_fixture


@pytest.mark.asyncio
async def test_search_gate_with_key(create_mock_client):
    data = load_fixture("search_polyester.json")
    captured_request = None

    async def handler(request: httpx.Request) -> httpx.Response:
        nonlocal captured_request
        captured_request = request
        return httpx.Response(200, json=data)

    client = create_mock_client(handler)
    client.settings.typesense_api_key = "test_typesense_key"
    resp = await search(client, "Polyester")

    assert captured_request is not None
    assert str(captured_request.url).startswith("https://gate.fintables.com/search/multi_search")
    assert captured_request.url.params.get("q") == "Polyester"
    assert captured_request.headers.get("x-typesense-api-key") == "test_typesense_key"
    body = json.loads(captured_request.content)
    assert "searches" in body
    assert len(body["searches"]) == 4

    assert len(resp.results) == 4
    equities = resp.results[0]
    assert equities.found == 2
    assert len(equities.hits) == 2
    assert equities.hits[0].document.code == "KOPOL"
    assert equities.hits[1].document.code == "SASA"
    assert "xu100" in equities.hits[1].document.flags

    warrants = resp.results[2]
    assert warrants.found == 235
    assert len(warrants.hits) == 1
    assert warrants.hits[0].document.code == "SL1KM.V"


@pytest.mark.asyncio
async def test_search_mobile_fallback(create_mock_client):
    captured_request = None

    async def handler(request: httpx.Request) -> httpx.Response:
        nonlocal captured_request
        captured_request = request
        return httpx.Response(
            200,
            json={
                "results": [
                    {
                        "title": "Şirketler",
                        "symbols": [
                            {
                                "code": "KOPOL",
                                "type": "equity",
                                "title": "Koza Polyester",
                                "flags": ["xu100"],
                            }
                        ],
                    }
                ]
            },
        )

    client = create_mock_client(handler)
    client.settings.typesense_api_key = None
    resp = await search(client, "Polyester")

    assert captured_request is not None
    assert "/mobile/search/" in str(captured_request.url)
    assert captured_request.url.params.get("q") == "Polyester"
    assert len(resp.results) == 1
    assert resp.results[0].title == "Şirketler"
    assert resp.results[0].hits[0].document.code == "KOPOL"
