from fintables.api.client import FintablesClient
from fintables.models.analyst_rating import AnalystRatingList


async def get_analyst_ratings(
    client: FintablesClient,
    ticker: str,
    brokerage_id: str | None = None,
    in_model_portfolio: bool | None = None,
) -> AnalystRatingList:
    """Fetches analyst ratings for a given symbol."""
    ticker_clean = ticker.strip().upper()
    params: dict[str, str] = {
        "code": ticker_clean,
        "brokerage_id": brokerage_id or "",
    }
    if in_model_portfolio is not None:
        params["in_model_portfolio"] = "true" if in_model_portfolio else "false"
    else:
        params["in_model_portfolio"] = ""

    response = await client.get("/analyst-ratings/", params=params)
    data = response.json()
    if isinstance(data, list):
        return AnalystRatingList(results=data)
    return AnalystRatingList.model_validate(data)
