from fintables.api.client import FintablesClient
from fintables.models.notification import (
    MarkAsReadResponse,
    NotificationPage,
    NotificationUnreadStatus,
)


async def list_notifications(
    client: FintablesClient,
    page_size: int = 100,
) -> NotificationPage:
    """Fetches user notifications."""
    params: dict[str, str | int] = {
        "page_size": page_size,
    }

    response = await client.get(
        "/notifications/",
        params=params,
        requires_auth=True,
    )
    return NotificationPage.model_validate(response.json())


async def get_unread_status(client: FintablesClient) -> NotificationUnreadStatus:
    """Checks whether the user has unread notifications and returns the last read timestamp."""
    response = await client.get(
        "/notifications/unread_count/",
        requires_auth=True,
    )
    return NotificationUnreadStatus.model_validate(response.json())


async def mark_notifications_as_read(client: FintablesClient) -> MarkAsReadResponse:
    """Marks all user notifications as read."""
    response = await client.post(
        "/notifications/mark_as_read/",
        requires_auth=True,
    )
    return MarkAsReadResponse.model_validate(response.json())
