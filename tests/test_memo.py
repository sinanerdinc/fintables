import httpx
import pytest

from fintables.api.endpoints.memo import (
    create_memo,
    delete_memo,
    list_memos,
    update_memo,
)


@pytest.mark.asyncio
async def test_list_memos(create_mock_client):
    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json=[
                {
                    "id": 42212,
                    "code": "FROTO",
                    "created_at": "2026-09-15T19:27:39.446002Z",
                    "updated_at": "2026-09-15T19:27:39.446023Z",
                    "content": "Not içeriği",
                }
            ],
        )

    client = create_mock_client(handler)
    memos = await list_memos(client)
    assert len(memos) == 1
    assert memos[0].id == 42212
    assert memos[0].code == "FROTO"
    assert memos[0].content == "Not içeriği"


@pytest.mark.asyncio
async def test_create_memo(create_mock_client):
    captured_request = None

    async def handler(request: httpx.Request) -> httpx.Response:
        nonlocal captured_request
        captured_request = request
        return httpx.Response(
            200,
            json={
                "id": 42212,
                "code": "FROTO",
                "created_at": "2026-09-15T19:27:39.446002Z",
                "updated_at": "2026-09-15T19:27:39.446023Z",
                "content": "Yeni not",
            },
        )

    client = create_mock_client(handler)
    memo = await create_memo(client, "FROTO", "Yeni not")

    assert captured_request.method == "POST"
    assert memo.id == 42212
    assert memo.content == "Yeni not"


@pytest.mark.asyncio
async def test_update_memo(create_mock_client):
    captured_request = None

    async def handler(request: httpx.Request) -> httpx.Response:
        nonlocal captured_request
        captured_request = request
        return httpx.Response(
            200,
            json={
                "id": 42212,
                "code": "FROTO",
                "created_at": "2026-09-15T19:27:39.446002Z",
                "updated_at": "2026-09-15T19:29:53.259914Z",
                "content": "Güncellendi",
            },
        )

    client = create_mock_client(handler)
    memo = await update_memo(client, 42212, "FROTO", "Güncellendi")

    assert captured_request.method == "PUT"
    assert "/memos/42212/" in str(captured_request.url)
    assert memo.content == "Güncellendi"


@pytest.mark.asyncio
async def test_delete_memo(create_mock_client):
    captured_request = None

    async def handler(request: httpx.Request) -> httpx.Response:
        nonlocal captured_request
        captured_request = request
        return httpx.Response(204)

    client = create_mock_client(handler)
    await delete_memo(client, 42212)

    assert captured_request.method == "DELETE"
    assert "/memos/42212/" in str(captured_request.url)
