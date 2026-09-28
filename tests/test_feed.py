import httpx
import pytest

from fintables.api.endpoints.feed import get_feed
from fintables.models.feed import ArticleItem, NewsItem, NewsletterItem, PostItem
from tests.conftest import load_fixture


@pytest.mark.asyncio
async def test_get_feed(create_mock_client):
    data = load_fixture("feed_froto.json")
    captured_request = None

    async def handler(request: httpx.Request) -> httpx.Response:
        nonlocal captured_request
        captured_request = request
        return httpx.Response(200, json=data)

    client = create_mock_client(handler)
    page = await get_feed(client, "FROTO", page_size=30)

    assert "/topic-feed/" in str(captured_request.url)
    assert captured_request.headers["Authorization"] == "Bearer test_access_token"
    assert captured_request.url.params.get("symbols") == "FROTO"
    assert captured_request.url.params.get("page_size") == "30"

    assert len(page.results) == 4
    item0 = page.results[0]
    assert isinstance(item0, PostItem)
    assert item0.type == "post"
    assert item0.importance == "mid"

    item1 = page.results[1]
    assert isinstance(item1, NewsItem)
    assert item1.type == "news"
    assert item1.importance == "high"
    assert item1.news.note == "Ford Trucks 364M Euro yatırım"

    item2 = page.results[2]
    assert isinstance(item2, NewsletterItem)
    assert item2.type == "newsletter"

    item3 = page.results[3]
    assert isinstance(item3, ArticleItem)
    assert item3.type == "article"
