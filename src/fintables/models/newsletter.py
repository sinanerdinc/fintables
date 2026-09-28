from datetime import datetime
from typing import Any
from pydantic import BaseModel


class NewsletterAuthor(BaseModel):
    slug: str | None = None
    name: str
    bio: str | None = None
    avatar: str | None = None
    banner: str | None = None
    title: str | None = None


class NewsletterCategory(BaseModel):
    slug: str | None = None
    title: str
    description: str | None = None
    main_category: str | None = None


class NewsletterListItem(BaseModel):
    id: str
    slug: str
    author: NewsletterAuthor | None = None
    title: str
    created_at: datetime | None = None
    published_at: datetime | None = None
    category: NewsletterCategory | None = None


class NewsletterPage(BaseModel):
    count: int = 0
    next: str | None = None
    previous: str | None = None
    results: list[NewsletterListItem] = []


class EditorBlock(BaseModel):
    id: str | None = None
    type: str
    data: dict[str, Any] = {}


class EditorContent(BaseModel):
    time: int | None = None
    blocks: list[EditorBlock] = []
    version: str | None = None


class NewsletterDetail(BaseModel):
    id: str
    slug: str
    author: NewsletterAuthor | None = None
    title: str
    created_at: datetime | None = None
    published_at: datetime | None = None
    category: NewsletterCategory | None = None
    content: EditorContent | None = None
