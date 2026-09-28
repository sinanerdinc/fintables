from datetime import datetime
from pydantic import BaseModel


class Notification(BaseModel):
    id: int
    created_at: datetime
    message: str
    app_url: str | None = None
    web_url: str | None = None


class NotificationPage(BaseModel):
    next: str | None = None
    previous: str | None = None
    results: list[Notification] = []


class NotificationUnreadStatus(BaseModel):
    read_at: datetime | None = None
    has_unread: bool


class MarkAsReadResponse(BaseModel):
    status: str
