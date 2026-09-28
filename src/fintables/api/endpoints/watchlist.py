from fintables.api.client import FintablesClient
from fintables.models.watchlist import WatchlistResponse


async def add_favorite(client: FintablesClient, ticker: str) -> WatchlistResponse:
    """Adds a symbol to favorites watchlist."""
    ticker_clean = ticker.strip().upper()
    response = await client.post(
        f"/watchlists/favorites/items/{ticker_clean}/",
        requires_auth=True,
    )
    return WatchlistResponse.model_validate(response.json())


async def remove_favorite(client: FintablesClient, ticker: str) -> WatchlistResponse:
    """Removes a symbol from favorites watchlist."""
    ticker_clean = ticker.strip().upper()
    response = await client.delete(
        f"/watchlists/favorites/items/{ticker_clean}/",
        requires_auth=True,
    )
    return WatchlistResponse.model_validate(response.json())
