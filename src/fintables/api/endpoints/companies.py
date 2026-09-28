from fintables.api.client import FintablesClient
from fintables.models.company import Company


async def get_company(client: FintablesClient, ticker: str) -> Company:
    """Fetches company profile and ratio types."""
    ticker_clean = ticker.strip().upper()
    response = await client.get(f"/companies/{ticker_clean}/")
    return Company.model_validate(response.json())
