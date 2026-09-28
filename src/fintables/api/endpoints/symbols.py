from fintables.api.client import FintablesClient
from fintables.models.symbol import SymbolSummary


async def get_symbol_summary(client: FintablesClient, ticker: str) -> SymbolSummary:
    """Fetches symbol summary including multipliers, financial summary, and yield analysis."""
    ticker_clean = ticker.strip().upper()
    response = await client.get(f"/mobile/symbols/{ticker_clean}/summary/")
    return SymbolSummary.model_validate(response.json())
