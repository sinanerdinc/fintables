import httpx
import pytest

from fintables.api.auth import login, refresh_token
from fintables.exceptions import AuthError


@pytest.mark.asyncio
async def test_login_success():
    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"access": "test_access", "refresh": "test_refresh"})

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    access, refresh = await login(client, "user", "pass")
    assert access == "test_access"
    assert refresh == "test_refresh"


@pytest.mark.asyncio
async def test_login_failure():
    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(400, json={"detail": "Bad credentials"})

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    with pytest.raises(AuthError):
        await login(client, "user", "wrong")


@pytest.mark.asyncio
async def test_refresh_token_success():
    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"access": "new_access"})

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    new_access = await refresh_token(client, "test_refresh")
    assert new_access == "new_access"


@pytest.mark.asyncio
async def test_refresh_token_failure():
    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(401, json={"detail": "Token expired"})

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    with pytest.raises(AuthError):
        await refresh_token(client, "bad_refresh")
