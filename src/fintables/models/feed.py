from datetime import datetime
from typing import Annotated, Any, Literal
from pydantic import BaseModel, Field


class FeedTopic(BaseModel):
    type: str
    title: str | None = None
    id: int | str | None = None
    slug: str | None = None


class PostContent(BaseModel):
    body: str | None = None
    link: str | None = None
    attachments: list[Any] = []
    content: Any = None


class PostItem(BaseModel):
    type: Literal["post"] = "post"
    id: str
    slug: str | None = None
    title: str
    date: datetime
    importance: str | None = None
    highlight: bool = False
    pinned: bool = False
    post: PostContent
    topics: list[FeedTopic] = []


class KapSymbol(BaseModel):
    code: str
    type: str | None = None


class NewsDetail(BaseModel):
    id: str
    published_at: datetime
    kap_id: int | None = None
    title: str
    symbols: list[KapSymbol] = []
    companies: list[str] = []
    related_companies: list[str] = []
    type: str | None = None
    summary: str | None = None
    subject: str | None = None
    embed_url: str | None = None
    attachments: list[Any] = []
    note: str | None = None
    note_title: str | None = None


class NewsItem(BaseModel):
    type: Literal["news"] = "news"
    id: str
    slug: str | None = None
    title: str
    subtitle: str | None = None
    date: datetime
    importance: str | None = None
    pinned: bool = False
    news: NewsDetail
    topics: list[FeedTopic] = []


class NewsletterAuthor(BaseModel):
    slug: str | None = None
    name: str
    bio: str | None = None
    avatar: str | None = None
    title: str | None = None


class NewsletterCategory(BaseModel):
    slug: str | None = None
    title: str
    description: str | None = None
    main_category: str | None = None


class NewsletterDetail(BaseModel):
    id: str | int
    slug: str | None = None
    author: NewsletterAuthor | None = None
    title: str
    created_at: datetime | None = None
    published_at: datetime | None = None
    category: NewsletterCategory | None = None


class NewsletterItem(BaseModel):
    type: Literal["newsletter"] = "newsletter"
    id: str
    slug: str | None = None
    title: str
    date: datetime
    newsletter: NewsletterDetail
    topics: list[FeedTopic] = []


class ArticleCategory(BaseModel):
    id: int | None = None
    slug: str | None = None
    title: str
    description: str | None = None
    main_category: str | None = None


class ArticleDetail(BaseModel):
    id: int | str
    slug: str | None = None
    title: str
    excerpt: str | None = None
    category: ArticleCategory | None = None
    cover: str | None = None
    read_time: int | None = None
    author: NewsletterAuthor | None = None
    description: str | None = None
    pdf_attachment: str | None = None


class ArticleItem(BaseModel):
    type: Literal["article"] = "article"
    id: str
    slug: str | None = None
    title: str
    date: datetime
    article: ArticleDetail
    topics: list[FeedTopic] = []


FeedItem = Annotated[
    PostItem | NewsItem | NewsletterItem | ArticleItem,
    Field(discriminator="type"),
]


class FeedPage(BaseModel):
    next: str | None = None
    previous: str | None = None
    results: list[FeedItem] = []
