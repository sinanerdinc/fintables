from datetime import datetime
from pydantic import BaseModel


class VideoSeries(BaseModel):
    slug: str | None = None
    title: str | None = None
    description: str | None = None
    cover: str | None = None
    main_category: str | None = None


class VideoItem(BaseModel):
    slug: str
    title: str
    cover: str | None = None
    description: str | None = None
    duration: str | None = None
    youtube_url: str | None = None
    series: VideoSeries | None = None
    published_at: datetime | None = None
    type: str | None = None


class VideoPage(BaseModel):
    count: int = 0
    next: str | None = None
    previous: str | None = None
    results: list[VideoItem] = []
