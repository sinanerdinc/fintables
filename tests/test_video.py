import httpx
import pytest

from fintables.api.endpoints.video import get_video, list_videos
from fintables.models.video import VideoItem, VideoPage


SAMPLE_VIDEO_DATA = {
    "count": 1,
    "next": None,
    "previous": None,
    "results": [
        {
            "slug": "bilanco-donemini-kapatiyoruz-fintables-haftalik-sohbetler-149",
            "title": "Bilanço Dönemini Kapatıyoruz | Fintables Haftalık Sohbetler #149",
            "cover": "https://storage.fintables.com/media/uploads/thumbnails/bilanco-donemini-kapatiyoruz-fintables-haftalik-sohbetler-149.jpg",
            "description": "Serkan Fırtına ve Ali Cenk Gözen programda gündemi değerlendirdi.",
            "duration": "00:23:30",
            "youtube_url": "https://www.youtube.com/watch?v=wZ0IeOdqmKc",
            "series": {
                "slug": "haftalik-sohbetler",
                "title": "Haftalık Sohbetler",
                "description": "Haftalık gündem değerlendirmesi.",
                "cover": None,
                "main_category": "bist",
            },
            "published_at": "2026-08-23T07:00:01Z",
            "type": "video",
        }
    ],
}


@pytest.mark.asyncio
async def test_list_videos(create_mock_client):
    captured_request = None

    async def handler(request: httpx.Request) -> httpx.Response:
        nonlocal captured_request
        captured_request = request
        return httpx.Response(200, json=SAMPLE_VIDEO_DATA)

    client = create_mock_client(handler)
    page = await list_videos(client, main_category="bist", page=1)

    assert "/videos/" in str(captured_request.url)
    assert captured_request.url.params.get("main_category") == "bist"
    assert captured_request.url.params.get("type") == "video"
    assert captured_request.url.params.get("page") == "1"

    assert isinstance(page, VideoPage)
    assert page.count == 1
    assert len(page.results) == 1
    assert page.results[0].slug == "bilanco-donemini-kapatiyoruz-fintables-haftalik-sohbetler-149"
    assert page.results[0].series.title == "Haftalık Sohbetler"


@pytest.mark.asyncio
async def test_get_video(create_mock_client):
    captured_request = None

    async def handler(request: httpx.Request) -> httpx.Response:
        nonlocal captured_request
        captured_request = request
        return httpx.Response(200, json=SAMPLE_VIDEO_DATA["results"][0])

    client = create_mock_client(handler)
    item = await get_video(client, "bilanco-donemini-kapatiyoruz-fintables-haftalik-sohbetler-149")

    assert "/videos/bilanco-donemini-kapatiyoruz-fintables-haftalik-sohbetler-149/" in str(captured_request.url)
    assert isinstance(item, VideoItem)
    assert item.duration == "00:23:30"
    assert "youtube.com" in item.youtube_url
