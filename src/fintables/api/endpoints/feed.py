from fintables.api.client import FintablesClient
from fintables.models.feed import FeedPage


async def get_feed(
    client: FintablesClient,
    ticker: str,
    page_size: int = 30,
    cursor: str | None = None,
) -> FeedPage:
    """Fetches topic feed (news, posts, newsletter, articles) for a given symbol."""
    ticker_clean = ticker.strip().upper()
    params: dict[str, str | int] = {
        "symbols": ticker_clean,
        "for_everyone": 0,
        "page_size": page_size,
    }
    if cursor:
        params["cursor"] = cursor

    response = await client.get(
        "/topic-feed/",
        params=params,
        requires_auth=True,
    )
    return FeedPage.model_validate(response.json())


async def get_topic_feed(
    client: FintablesClient,
    page_size: int = 100,
    cursor: str | None = None,
) -> FeedPage:
    """Fetches global topic feed without a specific symbol."""
    params: dict[str, str | int] = {
        "only_pro": 1,
        "page_size": page_size,
    }
    if cursor:
        params["cursor"] = cursor

    response = await client.get(
        "/topic-feed/",
        params=params,
        requires_auth=True,
    )
    return FeedPage.model_validate(response.json())
