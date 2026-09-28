from datetime import datetime
from typing import Any
from pydantic import BaseModel

# EditorJS modelleri newsletter ile aynı yapı, oradan import et
from fintables.models.newsletter import (
    EditorBlock,
    EditorContent,
    NewsletterAuthor as PostAuthor,
)


class PostCategory(BaseModel):
    id: int | None = None
    slug: str | None = None
    title: str
    description: str | None = None
    og: str | None = None
    main_category: str | None = None


class PostListItem(BaseModel):
    id: int
    slug: str
    created_at: datetime | None = None
    title: str
    excerpt: str | None = None
    category: PostCategory | None = None
    cover: str | None = None
    og: str | None = None
    read_time: int | None = None
    author: PostAuthor | None = None
    description: str | None = None
    pdf_attachment: str | None = None


class PostPage(BaseModel):
    count: int = 0
    next: str | None = None
    previous: str | None = None
    results: list[PostListItem] = []


class PostDetail(PostListItem):
    content: EditorContent | None = None
    similars: list[PostListItem] = []
