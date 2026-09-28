import httpx
import pytest

from fintables.api.client import FintablesClient
from fintables.config import Settings
from fintables.exceptions import AuthError, NotFoundError


@pytest.mark.asyncio
async def test_client_headers_and_public_request(create_mock_client):
    captured_request = None

    async def handler(request: httpx.Request) -> httpx.Response:
        nonlocal captured_request
        captured_request = request
        return httpx.Response(200, json={"status": "ok"})

    client = create_mock_client(handler)
    resp = await client.get("/public/endpoint")

    assert resp.status_code == 200
    assert captured_request is not None
    assert captured_request.headers["User-Agent"] == "fintables-mobile/323 (2.28.2)"
    assert captured_request.headers["Host"] == "api.fintables.com"
    assert "Authorization" not in captured_request.headers


@pytest.mark.asyncio
async def test_client_auth_header(create_mock_client):
    captured_request = None

    async def handler(request: httpx.Request) -> httpx.Response:
        nonlocal captured_request
        captured_request = request
        return httpx.Response(200, json={"status": "ok"})

    client = create_mock_client(handler)
    await client.get("/auth/endpoint", requires_auth=True)

    assert captured_request is not None
    assert captured_request.headers["Authorization"] == "Bearer test_access_token"


@pytest.mark.asyncio
async def test_client_gate_headers(create_mock_client):
    captured_request = None

    async def handler(request: httpx.Request) -> httpx.Response:
        nonlocal captured_request
        captured_request = request
        return httpx.Response(200, json={"status": "ok"})

    client = create_mock_client(handler)
    await client.post("/search/multi_search", is_gate=True, json={})

    assert captured_request is not None
    assert str(captured_request.url).startswith("https://gate.fintables.com")
    assert captured_request.headers["Host"] == "gate.fintables.com"


@pytest.mark.asyncio
async def test_client_not_found(create_mock_client):
    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(404, text="Not Found")

    client = create_mock_client(handler)
    with pytest.raises(NotFoundError):
        await client.get("/nonexistent")


@pytest.mark.asyncio
async def test_client_401_retry_success(mock_settings):
    call_count = 0

    class MockTransport(httpx.AsyncBaseTransport):
        async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
            nonlocal call_count
            call_count += 1
            if "/auth/token/refresh/" in str(request.url):
                return httpx.Response(200, json={"access": "new_access_token"})
            if call_count == 1:
                return httpx.Response(401, json={"detail": "Token expired"})
            return httpx.Response(200, json={"data": "success"})

    async_client = httpx.AsyncClient(transport=MockTransport())
    client = FintablesClient(
        custom_settings=mock_settings,
        access_token="expired_token",
        refresh_token_val="valid_refresh_token",
        client=async_client,
    )

    resp = await client.get("/protected", requires_auth=True)
    assert resp.status_code == 200
    assert client._access_token == "new_access_token"


@pytest.mark.asyncio
async def test_client_auth_error_no_credentials():
    empty_settings = Settings(username=None, password=None)
    client = FintablesClient(custom_settings=empty_settings)
    with pytest.raises(AuthError):
        await client.get("/protected", requires_auth=True)
