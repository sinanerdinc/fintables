from datetime import datetime
from unittest.mock import AsyncMock, patch

import httpx
import pytest
from typer.testing import CliRunner

from fintables.api.endpoints.notifications import (
    get_unread_status,
    list_notifications,
    mark_notifications_as_read,
)
from fintables.cli.main import app
from fintables.models.notification import (
    MarkAsReadResponse,
    Notification,
    NotificationPage,
    NotificationUnreadStatus,
)
from fintables.output.formatter import (
    print_notification_action,
    print_notification_status,
    print_notifications_table,
)

runner = CliRunner()

MOCK_NOTIFICATIONS_DATA = {
    "next": "https://api.fintables.com/notifications/?cursor=cD04NzAzOQ%3D%3D&page_size=15",
    "previous": None,
    "results": [
        {
            "id": 88266,
            "created_at": "2026-09-22T15:05:06.813147Z",
            "message": "🔴 BIST 100 günü %-1,04 düşüşle kapattı.",
            "app_url": None,
            "web_url": None,
        },
        {
            "id": 88105,
            "created_at": "2026-09-22T06:00:04.641549Z",
            "message": "🔄 Endekslerde tarihi değişim",
            "app_url": "fintables://newsletters/endekslerde-tarihi-degisim",
            "web_url": "https://fintables.com/arastirma/bultenler/gunluk-bulten/endekslerde-tarihi-degisim",
        },
    ],
}

MOCK_UNREAD_DATA = {
    "read_at": "2025-07-28T19:21:52.641469Z",
    "has_unread": True,
}

MOCK_MARK_AS_READ_DATA = {
    "status": "success",
}


def test_notification_models():
    page = NotificationPage.model_validate(MOCK_NOTIFICATIONS_DATA)
    assert len(page.results) == 2
    assert page.results[0].id == 88266
    assert "BIST 100" in page.results[0].message
    assert page.results[1].app_url == "fintables://newsletters/endekslerde-tarihi-degisim"
    assert page.next is not None

    status = NotificationUnreadStatus.model_validate(MOCK_UNREAD_DATA)
    assert status.has_unread is True
    assert isinstance(status.read_at, datetime)

    mark_resp = MarkAsReadResponse.model_validate(MOCK_MARK_AS_READ_DATA)
    assert mark_resp.status == "success"


@pytest.mark.asyncio
async def test_list_notifications_endpoint(create_mock_client):
    captured_request = None

    async def handler(request: httpx.Request) -> httpx.Response:
        nonlocal captured_request
        captured_request = request
        return httpx.Response(200, json=MOCK_NOTIFICATIONS_DATA)

    client = create_mock_client(handler)
    page = await list_notifications(client, page_size=50)

    assert captured_request is not None
    assert captured_request.method == "GET"
    assert "/notifications/" in str(captured_request.url)
    assert "page_size=50" in str(captured_request.url)
    assert len(page.results) == 2


@pytest.mark.asyncio
async def test_get_unread_status_endpoint(create_mock_client):
    captured_request = None

    async def handler(request: httpx.Request) -> httpx.Response:
        nonlocal captured_request
        captured_request = request
        return httpx.Response(200, json=MOCK_UNREAD_DATA)

    client = create_mock_client(handler)
    status = await get_unread_status(client)

    assert captured_request is not None
    assert captured_request.method == "GET"
    assert "/notifications/unread_count/" in str(captured_request.url)
    assert status.has_unread is True


@pytest.mark.asyncio
async def test_mark_notifications_as_read_endpoint(create_mock_client):
    captured_request = None

    async def handler(request: httpx.Request) -> httpx.Response:
        nonlocal captured_request
        captured_request = request
        return httpx.Response(200, json=MOCK_MARK_AS_READ_DATA)

    client = create_mock_client(handler)
    resp = await mark_notifications_as_read(client)

    assert captured_request is not None
    assert captured_request.method == "POST"
    assert "/notifications/mark_as_read/" in str(captured_request.url)
    assert resp.status == "success"


def test_notification_formatters():
    page = NotificationPage.model_validate(MOCK_NOTIFICATIONS_DATA)
    print_notifications_table(page)

    # Empty page test
    empty_page = NotificationPage(results=[])
    print_notifications_table(empty_page)

    # Status formatter tests
    status_unread = NotificationUnreadStatus(has_unread=True, read_at=datetime.now())
    print_notification_status(status_unread)

    status_read = NotificationUnreadStatus(has_unread=False, read_at=None)
    print_notification_status(status_read)

    # Action formatter
    print_notification_action(action="mark_read", status="success")
    print_notification_action(action="mark_read", status="failed")


@patch("fintables.cli.commands.notification.list_notifications", new_callable=AsyncMock)
def test_cli_notification_list(mock_list):
    mock_list.return_value = NotificationPage.model_validate(MOCK_NOTIFICATIONS_DATA)

    result = runner.invoke(app, ["notification", "list"])
    assert result.exit_code == 0
    assert "88266" in result.stdout
    assert "BIST 100" in result.stdout

    result_json = runner.invoke(app, ["notification", "list", "--output", "json"])
    assert result_json.exit_code == 0
    assert "88266" in result_json.stdout


@patch("fintables.cli.commands.notification.get_unread_status", new_callable=AsyncMock)
def test_cli_notification_unread(mock_status):
    mock_status.return_value = NotificationUnreadStatus.model_validate(MOCK_UNREAD_DATA)

    result = runner.invoke(app, ["notification", "unread"])
    assert result.exit_code == 0
    assert "You have unread notifications" in result.stdout

    result_status = runner.invoke(app, ["notification", "status"])
    assert result_status.exit_code == 0
    assert "You have unread notifications" in result_status.stdout

    result_json = runner.invoke(app, ["notification", "unread", "--output", "json"])
    assert result_json.exit_code == 0
    assert '"has_unread": true' in result_json.stdout


@patch("fintables.cli.commands.notification.mark_notifications_as_read", new_callable=AsyncMock)
def test_cli_notification_mark_read(mock_mark):
    mock_mark.return_value = MarkAsReadResponse.model_validate(MOCK_MARK_AS_READ_DATA)

    result = runner.invoke(app, ["notification", "mark-read"])
    assert result.exit_code == 0
    assert "marked as read" in result.stdout

    result_json = runner.invoke(app, ["notification", "mark-read", "--output", "json"])
    assert result_json.exit_code == 0
    assert '"status": "success"' in result_json.stdout
