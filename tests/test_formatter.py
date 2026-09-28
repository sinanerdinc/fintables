from fintables.models.analyst_rating import RatingType
from fintables.models.symbol import DataItem, ValueFormat
from fintables.output.formatter import (
    abbreviate_number,
    format_data_item,
    rating_type_badge,
)


def test_abbreviate_number():
    assert abbreviate_number(1_719_120_000_000, 2) == "1.72T"
    assert abbreviate_number(88_494_252_000, 1) == "88.5B"
    assert abbreviate_number(4_560_000_000, 2) == "4.56B"
    assert abbreviate_number(1_200_000, 2) == "1.20M"
    assert abbreviate_number(1_500, 1) == "1.5K"
    assert abbreviate_number(12.3456, 2) == "12.35"
    assert abbreviate_number(-1_500_000, 2) == "-1.50M"
    assert abbreviate_number(None) == "—"


def test_format_data_item():
    item_pct = DataItem(
        title="Dolaşım",
        value="25.78",
        type="percentage",
        format=ValueFormat(decimals=2),
    )
    assert format_data_item(item_pct) == "25.78%"

    item_curr = DataItem(
        title="Satışlar",
        value="88494252000",
        type="currency",
        format=ValueFormat(decimals=2, abbreviation=True),
    )
    assert format_data_item(item_curr) == "88.49B"

    item_none = DataItem(
        title="Boş",
        value=None,
        type="number",
        format=ValueFormat(nullToNa=True),
    )
    assert format_data_item(item_none) == "—"


def test_rating_type_badge():
    badge_al = rating_type_badge(RatingType.AL)
    assert "BUY" in badge_al
    assert "green" in badge_al

    badge_none = rating_type_badge(None)
    assert "—" in badge_none


def test_print_formatter_functions():
    from fintables.models.company import Company
    from fintables.models.symbol import SymbolSummary
    from fintables.models.analyst_rating import AnalystRatingList
    from fintables.models.search import SearchResponse
    from fintables.models.sheets import Sheets
    from fintables.models.feed import FeedPage
    from fintables.models.watchlist import WatchlistResponse
    from fintables.models.memo import Memo
    from datetime import datetime
    from tests.conftest import load_fixture
    from fintables.output.formatter import (
        print_company_table,
        print_symbol_summary_table,
        print_analyst_ratings_table,
        print_sheets_table,
        print_feed_table,
        print_watchlist,
        print_search_results,
        print_memos_table,
        print_memo_action,
        print_json,
    )

    # Company
    comp = Company.model_validate(load_fixture("company_asels.json"))
    print_company_table(comp)
    print_json(comp)

    # Symbol Summary
    summary = SymbolSummary.model_validate(load_fixture("symbol_summary_asels.json"))
    print_symbol_summary_table(summary)

    # Analyst
    ratings = AnalystRatingList.model_validate(load_fixture("analyst_ratings_asels.json"))
    print_analyst_ratings_table(ratings, "ASELS", brokerage_filter="PHC", model_portfolio_only=False)
    print_analyst_ratings_table(ratings, "ASELS", model_portfolio_only=True)

    # Sheets
    sheets = Sheets.model_validate(load_fixture("sheets_froto.json"))
    print_sheets_table(sheets, "FROTO", sheet_name="all", periods=2, quarterly=False)
    print_sheets_table(sheets, "FROTO", sheet_name="balance", periods=1, quarterly=True)

    # Feed
    feed = FeedPage.model_validate(load_fixture("feed_froto.json"))
    print_feed_table(feed, "FROTO", type_filter="post", importance_filter="mid")
    print_feed_table(feed, "FROTO", type_filter="news")

    # Watchlist
    wl = WatchlistResponse(watchlist={"id": "favorites", "name": "Favoriler", "is_default": True, "items": ["FROTO"]})
    print_watchlist(wl, action="add", ticker="FROTO")
    print_watchlist(wl, action="remove", ticker="FROTO")

    # Search
    sr = SearchResponse.model_validate(load_fixture("search_polyester.json"))
    print_search_results(sr, "Polyester")

    # Memo
    memo = Memo(id=1, code="FROTO", content="Test", created_at=datetime.now(), updated_at=datetime.now())
    print_memos_table([memo], ticker_filter="FROTO")
    print_memo_action("add", 1, "FROTO", "Test")
    print_memo_action("update", 1, "FROTO", "Test 2")
    print_memo_action("delete", 1)
