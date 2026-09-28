import httpx
import pytest

from fintables.api.endpoints.watchlist import add_favorite, remove_favorite


@pytest.mark.asyncio
async def test_add_favorite(create_mock_client):
    captured_request = None

    async def handler(request: httpx.Request) -> httpx.Response:
        nonlocal captured_request
        captured_request = request
        return httpx.Response(
            200,
            json={
                "watchlist": {
                    "id": "favorites",
                    "name": "Favoriler",
                    "is_default": True,
                    "items": ["FROTO"],
                }
            },
        )

    client = create_mock_client(handler)
    resp = await add_favorite(client, "FROTO")

    assert captured_request.method == "POST"
    assert "/watchlists/favorites/items/FROTO/" in str(captured_request.url)
    assert resp.watchlist.id == "favorites"
    assert resp.watchlist.items == ["FROTO"]


@pytest.mark.asyncio
async def test_remove_favorite(create_mock_client):
    captured_request = None

    async def handler(request: httpx.Request) -> httpx.Response:
        nonlocal captured_request
        captured_request = request
        return httpx.Response(
            200,
            json={
                "watchlist": {
                    "id": "favorites",
                    "name": "Favoriler",
                    "is_default": True,
                    "items": [],
                }
            },
        )

    client = create_mock_client(handler)
    resp = await remove_favorite(client, "FROTO")

    assert captured_request.method == "DELETE"
    assert "/watchlists/favorites/items/FROTO/" in str(captured_request.url)
    assert resp.watchlist.items == []
