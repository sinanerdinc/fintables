import pytest
from fintables.mcp.server import mcp


@pytest.mark.asyncio
async def test_all_mcp_tools_registration():
    """Tüm FastMCP araçlarının (23 adet tool) eksiksiz olarak kaydedildiğini doğrular."""
    tools = await mcp.list_tools()
    assert tools is not None

    tool_names = [tool.name for tool in tools]

    # 1. Arama & Şirket & Sembol Araçları
    assert "search_market" in tool_names
    assert "get_company_profile" in tool_names
    assert "get_stock_summary" in tool_names
    assert "get_financial_statements" in tool_names
    assert "get_analyst_forecasts" in tool_names

    # 2. Akış, Fon & Ajanda Araçları
    assert "get_news_feed" in tool_names
    assert "get_fund_details" in tool_names
    assert "get_economic_agenda" in tool_names

    # 3. Favoriler Araçları
    assert "add_stock_to_favorites" in tool_names
    assert "remove_stock_from_favorites" in tool_names

    # 4. Notlar (Memo) CRUD Araçları
    assert "get_user_memos" in tool_names
    assert "save_user_memo" in tool_names
    assert "update_user_memo" in tool_names
    assert "delete_user_memo" in tool_names

    # 5. Portföy CRUD & İşlem Araçları
    assert "get_user_portfolios" in tool_names
    assert "create_new_portfolio" in tool_names
    assert "update_portfolio_name" in tool_names
    assert "delete_user_portfolio" in tool_names
    assert "get_portfolio_positions" in tool_names
    assert "add_portfolio_transaction" in tool_names

    # 6. Bültenler, Yazılar, Videolar & Bildirimler
    assert "get_newsletters" in tool_names
    assert "read_newsletter" in tool_names
    assert "get_research_posts" in tool_names
    assert "read_research_post" in tool_names
    assert "get_videos" in tool_names
    assert "get_video_details" in tool_names
    assert "get_user_notifications" in tool_names
    assert "mark_all_notifications_read" in tool_names


@pytest.mark.asyncio
async def test_mcp_tool_execution_structure():
    """FastMCP araçlarının callable olduğunu ve araç listesinde schema tanımlarının bulunduğunu doğrular."""
    tools = await mcp.list_tools()
    search_tool = next((t for t in tools if t.name == "search_market"), None)
    assert search_tool is not None
    assert search_tool.description is not None
    assert "query" in str(search_tool.parameters)
