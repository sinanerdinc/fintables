from pydantic import BaseModel


class Watchlist(BaseModel):
    id: str
    name: str
    is_default: bool = False
    items: list[str] = []


class WatchlistResponse(BaseModel):
    watchlist: Watchlist
