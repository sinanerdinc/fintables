from typing import Any
from fastmcp import FastMCP

from fintables.api.client import FintablesClient
from fintables.api.endpoints.agenda import AgendaTime
from fintables.api.endpoints import (
    # Agenda
    get_agenda,
    # Analyst Ratings
    get_analyst_ratings,
    # Company & Symbols
    get_company,
    get_sheets,
    get_symbol_summary,
    # Feed
    get_feed,
    get_topic_feed,
    # Funds
    get_fund,
    get_fund_info,
    # Newsletters
    get_newsletter,
    list_newsletters,
    # Notifications
    get_unread_status,
    list_notifications,
    mark_notifications_as_read,
    # Memos
    create_memo,
    delete_memo,
    list_memos,
    update_memo,
    # Portfolios
    add_transaction,
    create_portfolio,
    delete_portfolio,
    get_positions,
    list_portfolios,
    update_portfolio,
    # Posts
    get_post,
    list_posts,
    # Search
    search,
    # Videos
    get_video,
    list_videos,
    # Favorites
    add_favorite,
    remove_favorite,
)

mcp = FastMCP("Fintables")


@mcp.tool()
async def search_market(query: str) -> dict[str, Any]:
    """Searches stock market items (stocks, futures, warrants, funds) by query string."""
    async with FintablesClient() as client:
        res = await search(client, query)
        return res.model_dump(by_alias=True)


@mcp.tool()
async def get_company_profile(ticker: str) -> dict[str, Any]:
    """Fetches general profile, inflation accounting status, katilim index status, and ratio types for a given company symbol (e.g. ASELS, FROTO)."""
    async with FintablesClient() as client:
        res = await get_company(client, ticker)
        return res.model_dump(by_alias=True)


@mcp.tool()
async def get_stock_summary(ticker: str) -> dict[str, Any]:
    """Fetches comprehensive summary for a symbol including price, valuation multipliers, sector info, and financial statement highlights."""
    async with FintablesClient() as client:
        res = await get_symbol_summary(client, ticker)
        return res.model_dump(by_alias=True)


@mcp.tool()
async def get_financial_statements(ticker: str) -> dict[str, Any]:
    """Fetches full financial statements (balance sheet, income statement, cash flow statement) for a company symbol."""
    async with FintablesClient() as client:
        res = await get_sheets(client, ticker)
        return res.model_dump(by_alias=True)


@mcp.tool()
async def get_analyst_forecasts(ticker: str) -> dict[str, Any]:
    """Fetches institutional analyst forecasts, ratings (BUY/HOLD/SELL), and target prices for a stock symbol."""
    async with FintablesClient() as client:
        res = await get_analyst_ratings(client, ticker)
        return res.model_dump(by_alias=True)


@mcp.tool()
async def get_news_feed(ticker: str | None = None, page_size: int = 30) -> dict[str, Any]:
    """Fetches latest news feed, disclosures (KAP), research notes, and market updates for a stock or overall market."""
    async with FintablesClient() as client:
        if ticker:
            res = await get_feed(client, ticker=ticker, page_size=page_size)
        else:
            res = await get_topic_feed(client, page_size=page_size)
        return res.model_dump(by_alias=True)


@mcp.tool()
async def get_fund_details(fund_code: str) -> dict[str, Any]:
    """Fetches mutual fund details, historical yields, risk score, asset allocation, and portfolio breakdown (e.g. TLY, MAC)."""
    async with FintablesClient() as client:
        fund_data = await get_fund(client, fund_code)
        fund_info = await get_fund_info(client, fund_code)
        return {
            "details": fund_data.model_dump(by_alias=True),
            "breakdown": fund_info.model_dump(by_alias=True),
        }


@mcp.tool()
async def get_economic_agenda(time_range: AgendaTime = "today") -> list[dict[str, Any]]:
    """Fetches economic calendar, dividend agenda, and macro events for a given time range ('today', 'thisWeek', 'nextWeek')."""
    async with FintablesClient() as client:
        res = await get_agenda(client, time=time_range)
        return [item.model_dump(by_alias=True) for item in res]


@mcp.tool()
async def add_stock_to_favorites(ticker: str) -> dict[str, Any]:
    """Adds a stock symbol to user's favorite watchlist (requires auth credentials)."""
    async with FintablesClient() as client:
        res = await add_favorite(client, ticker)
        return res.model_dump(by_alias=True)


@mcp.tool()
async def remove_stock_from_favorites(ticker: str) -> dict[str, Any]:
    """Removes a stock symbol from user's favorite watchlist (requires auth credentials)."""
    async with FintablesClient() as client:
        res = await remove_favorite(client, ticker)
        return res.model_dump(by_alias=True)


@mcp.tool()
async def get_user_memos() -> list[dict[str, Any]]:
    """Lists all personal memos and notes attached to stocks by the user (requires auth credentials)."""
    async with FintablesClient() as client:
        res = await list_memos(client)
        return [item.model_dump(by_alias=True) for item in res]


@mcp.tool()
async def save_user_memo(ticker: str, content: str) -> dict[str, Any]:
    """Creates a new personal note/memo attached to a stock symbol (requires auth credentials)."""
    async with FintablesClient() as client:
        res = await create_memo(client, code=ticker, content=content)
        return res.model_dump(by_alias=True)


@mcp.tool()
async def update_user_memo(memo_id: int, ticker: str, content: str) -> dict[str, Any]:
    """Updates an existing personal note/memo by its memo ID (requires auth credentials)."""
    async with FintablesClient() as client:
        res = await update_memo(client, memo_id=memo_id, code=ticker, content=content)
        return res.model_dump(by_alias=True)


@mcp.tool()
async def delete_user_memo(memo_id: int) -> dict[str, str]:
    """Deletes a personal note/memo by its memo ID (requires auth credentials)."""
    async with FintablesClient() as client:
        await delete_memo(client, memo_id=memo_id)
        return {"status": "success", "message": f"Memo {memo_id} deleted successfully."}


@mcp.tool()
async def get_user_portfolios() -> dict[str, Any]:
    """Lists virtual portfolios of the user with total values and positions (requires auth credentials)."""
    async with FintablesClient() as client:
        res = await list_portfolios(client)
        return res.model_dump(by_alias=True)


@mcp.tool()
async def create_new_portfolio(title: str) -> dict[str, Any]:
    """Creates a new virtual portfolio with a given title (requires auth credentials)."""
    async with FintablesClient() as client:
        res = await create_portfolio(client, title=title)
        return res.model_dump(by_alias=True)


@mcp.tool()
async def update_portfolio_name(portfolio_id: str, new_title: str) -> dict[str, Any]:
    """Renames an existing virtual portfolio (requires auth credentials)."""
    async with FintablesClient() as client:
        res = await update_portfolio(client, portfolio_id=portfolio_id, new_title=new_title)
        return res.model_dump(by_alias=True)


@mcp.tool()
async def delete_user_portfolio(portfolio_id: str) -> dict[str, str]:
    """Deletes a virtual portfolio by its UUID (requires auth credentials)."""
    async with FintablesClient() as client:
        await delete_portfolio(client, portfolio_id=portfolio_id)
        return {"status": "success", "message": f"Portfolio {portfolio_id} deleted successfully."}


@mcp.tool()
async def get_portfolio_positions(portfolio_id: str) -> dict[str, Any]:
    """Fetches current stock positions, average cost, current price, and gain/loss details for a portfolio UUID."""
    async with FintablesClient() as client:
        res = await get_positions(client, portfolio_id=portfolio_id)
        return res.model_dump(by_alias=True)


@mcp.tool()
async def add_portfolio_transaction(
    portfolio_id: str,
    ticker: str,
    side: str,
    amount: float,
    price: float,
    date: str,
) -> dict[str, Any]:
    """Adds a buy ('BUY') or sell ('SELL') transaction to a virtual portfolio (requires auth credentials)."""
    async with FintablesClient() as client:
        res = await add_transaction(
            client=client,
            portfolio_id=portfolio_id,
            code=ticker,
            side=side,
            amount=amount,
            price=price,
            date=date,
        )
        return res.model_dump(by_alias=True)


@mcp.tool()
async def get_newsletters(main_category: str = "bist", page: int = 1) -> dict[str, Any]:
    """Lists published newsletters (e.g. category 'bist') with summaries (requires auth credentials)."""
    async with FintablesClient() as client:
        res = await list_newsletters(client, main_category=main_category, page=page)
        return res.model_dump(by_alias=True)


@mcp.tool()
async def read_newsletter(slug: str) -> dict[str, Any]:
    """Fetches full content and details of a specific newsletter by its slug (requires auth credentials)."""
    async with FintablesClient() as client:
        res = await get_newsletter(client, slug=slug)
        return res.model_dump(by_alias=True)


@mcp.tool()
async def get_research_posts(main_category: str = "bist", page: int = 1) -> dict[str, Any]:
    """Lists research articles, company notes, and market analysis (requires auth credentials)."""
    async with FintablesClient() as client:
        res = await list_posts(client, main_category=main_category, page=page)
        return res.model_dump(by_alias=True)


@mcp.tool()
async def read_research_post(slug: str) -> dict[str, Any]:
    """Fetches full text and content of a specific research article/post by its slug (requires auth credentials)."""
    async with FintablesClient() as client:
        res = await get_post(client, slug=slug)
        return res.model_dump(by_alias=True)


@mcp.tool()
async def get_videos(main_category: str = "bist", page: int = 1) -> dict[str, Any]:
    """Lists stock market videos, weekly shows, and IPO analysis videos."""
    async with FintablesClient() as client:
        res = await list_videos(client, main_category=main_category, page=page)
        return res.model_dump(by_alias=True)


@mcp.tool()
async def get_video_details(slug: str) -> dict[str, Any]:
    """Fetches details and description of a specific video by slug."""
    async with FintablesClient() as client:
        res = await get_video(client, slug=slug)
        return res.model_dump(by_alias=True)


@mcp.tool()
async def get_user_notifications(page_size: int = 50) -> dict[str, Any]:
    """Lists user notifications and unread alert status (requires auth credentials)."""
    async with FintablesClient() as client:
        res = await list_notifications(client, page_size=page_size)
        unread = await get_unread_status(client)
        return {
            "notifications": res.model_dump(by_alias=True),
            "unread_status": unread.model_dump(by_alias=True),
        }


@mcp.tool()
async def mark_all_notifications_read() -> dict[str, Any]:
    """Marks all user notifications as read (requires auth credentials)."""
    async with FintablesClient() as client:
        res = await mark_notifications_as_read(client)
        return res.model_dump(by_alias=True)
