from fintables.api.client import FintablesClient
from fintables.models.fund import Fund, FundInfo

async def get_fund(client: FintablesClient, code: str) -> Fund:
    """Fetches general information about a fund."""
    code_clean = code.strip().upper()
    response = await client.get(f"/funds/{code_clean}/")
    return Fund.model_validate(response.json())

async def get_fund_info(client: FintablesClient, code: str) -> FundInfo:
    """Fetches detailed information and portfolio of a fund."""
    code_clean = code.strip().upper()
    response = await client.get(f"/funds/{code_clean}/info/")
    return FundInfo.model_validate(response.json())
