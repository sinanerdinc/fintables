from fintables.api.client import FintablesClient
from fintables.models.portfolio import Portfolio, PortfolioPage, PositionPage, Transaction


async def list_portfolios(
    client: FintablesClient,
    page_size: int = 100,
) -> PortfolioPage:
    """Kullanıcının sanal portföylerini listeler."""
    response = await client.get(
        "/portfolios/",
        params={"page_size": page_size},
        requires_auth=True,
    )
    return PortfolioPage.model_validate(response.json())


async def create_portfolio(
    client: FintablesClient,
    title: str,
) -> Portfolio:
    """Yeni bir sanal portföy oluşturur."""
    response = await client.post(
        "/portfolios/",
        json={"title": title},
        requires_auth=True,
    )
    return Portfolio.model_validate(response.json())


async def delete_portfolio(
    client: FintablesClient,
    portfolio_id: str,
) -> None:
    """Belirtilen sanal portföyü siler."""
    await client.delete(
        f"/portfolios/{portfolio_id}/",
        requires_auth=True,
    )


async def update_portfolio(
    client: FintablesClient,
    portfolio_id: str,
    new_title: str,
) -> Portfolio:
    """Portföy adını günceller."""
    response = await client.request(
        "PATCH",
        f"/portfolios/{portfolio_id}/",
        json={"id": portfolio_id, "title": new_title},
        requires_auth=True,
    )
    return Portfolio.model_validate(response.json())


async def get_positions(
    client: FintablesClient,
    portfolio_id: str,
) -> PositionPage:
    """Portföydeki pozisyonları (varlıkları) getirir."""
    response = await client.get(
        f"/portfolios/{portfolio_id}/positions/",
        requires_auth=True,
    )
    data = response.json()
    # API doğrudan liste de döndürebilir
    if isinstance(data, list):
        data = {"results": data}
    return PositionPage.model_validate(data)


async def add_transaction(
    client: FintablesClient,
    portfolio_id: str,
    code: str,
    side: str,
    amount: str | int | float,
    price: str | float,
    date: str,
) -> Transaction:
    """Portföye alış (BUY) veya satış (SELL) işlemi ekler."""
    payload = {
        "code": code.strip().upper(),
        "side": side.upper(),
        "amount": str(amount),
        "price": str(price),
        "date": date,
    }
    response = await client.post(
        f"/portfolios/{portfolio_id}/transactions/",
        json=payload,
        requires_auth=True,
    )
    return Transaction.model_validate(response.json())
