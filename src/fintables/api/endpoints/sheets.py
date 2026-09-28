from fintables.api.client import FintablesClient
from fintables.models.sheets import Sheets


async def get_sheets(client: FintablesClient, ticker: str) -> Sheets:
    """Fetches full financial sheets (balance, income, cashflow) for a given symbol."""
    ticker_clean = ticker.strip().upper()
    response = await client.get(
        f"/mobile/symbols/{ticker_clean}/sheets/",
        requires_auth=True,
    )
    return Sheets.model_validate(response.json())
