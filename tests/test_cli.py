from typer.testing import CliRunner
from unittest.mock import patch, AsyncMock
from fintables.cli.main import app
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

runner = CliRunner()


def test_cli_version():
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "fintables version" in result.stdout


def test_cli_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "company" in result.stdout
    assert "symbol" in result.stdout
    assert "analyst" in result.stdout
    assert "search" in result.stdout
    assert "feed" in result.stdout
    assert "watchlist" in result.stdout
    assert "memo" in result.stdout


@patch("fintables.cli.commands.company.get_company", new_callable=AsyncMock)
def test_cli_company(mock_get_company):
    mock_get_company.return_value = Company.model_validate(load_fixture("company_asels.json"))
    result = runner.invoke(app, ["company", "ASELS"])
    assert result.exit_code == 0
    assert "ASELS" in result.stdout

    result_json = runner.invoke(app, ["company", "ASELS", "--output", "json"])
    assert result_json.exit_code == 0
    assert '"code": "ASELS"' in result_json.stdout


@patch("fintables.cli.commands.symbol.get_symbol_summary", new_callable=AsyncMock)
def test_cli_symbol_summary(mock_summary):
    mock_summary.return_value = SymbolSummary.model_validate(load_fixture("symbol_summary_asels.json"))
    result = runner.invoke(app, ["symbol", "ASELS", "summary"])
    assert result.exit_code == 0
    assert ("Multipliers" in result.stdout or "Çarpanlar" in result.stdout)


@patch("fintables.cli.commands.symbol.get_sheets", new_callable=AsyncMock)
def test_cli_symbol_sheets(mock_sheets):
    mock_sheets.return_value = Sheets.model_validate(load_fixture("sheets_froto.json"))
    result = runner.invoke(app, ["symbol", "FROTO", "sheets"])
    assert result.exit_code == 0
    assert "Balance Sheet" in result.stdout


@patch("fintables.cli.commands.analyst.get_analyst_ratings", new_callable=AsyncMock)
def test_cli_analyst(mock_ratings):
    mock_ratings.return_value = AnalystRatingList.model_validate(load_fixture("analyst_ratings_asels.json"))
    result = runner.invoke(app, ["analyst", "ASELS"])
    assert result.exit_code == 0
    assert "ASELS" in result.stdout
    assert "Phillip" in result.stdout


@patch("fintables.cli.commands.search.search", new_callable=AsyncMock)
def test_cli_search(mock_search):
    mock_search.return_value = SearchResponse.model_validate(load_fixture("search_polyester.json"))
    result = runner.invoke(app, ["search", "Polyester"])
    assert result.exit_code == 0
    assert "KOPOL" in result.stdout
    assert "SASA" in result.stdout


@patch("fintables.cli.commands.feed.get_feed", new_callable=AsyncMock)
def test_cli_feed(mock_feed):
    mock_feed.return_value = FeedPage.model_validate(load_fixture("feed_froto.json"))
    result = runner.invoke(app, ["feed", "FROTO"])
    assert result.exit_code == 0
    assert "FROTO" in result.stdout


@patch("fintables.cli.commands.watchlist.add_favorite", new_callable=AsyncMock)
@patch("fintables.cli.commands.watchlist.remove_favorite", new_callable=AsyncMock)
def test_cli_watchlist(mock_remove, mock_add):
    mock_add.return_value = WatchlistResponse(watchlist={"id": "favorites", "name": "Favoriler", "is_default": True, "items": ["FROTO"]})
    result_add = runner.invoke(app, ["watchlist", "add", "FROTO"])
    assert result_add.exit_code == 0
    assert "added to watchlist" in result_add.stdout

    mock_remove.return_value = WatchlistResponse(watchlist={"id": "favorites", "name": "Favoriler", "is_default": True, "items": []})
    result_remove = runner.invoke(app, ["watchlist", "remove", "FROTO"])
    assert result_remove.exit_code == 0
    assert "removed from watchlist" in result_remove.stdout


@patch("fintables.cli.commands.memo.list_memos", new_callable=AsyncMock)
@patch("fintables.cli.commands.memo.create_memo", new_callable=AsyncMock)
@patch("fintables.cli.commands.memo.update_memo", new_callable=AsyncMock)
@patch("fintables.cli.commands.memo.delete_memo", new_callable=AsyncMock)
def test_cli_memo(mock_delete, mock_update, mock_create, mock_list):
    dummy_memo = Memo(id=42212, code="FROTO", content="Not içeriği", created_at=datetime.now(), updated_at=datetime.now())
    mock_list.return_value = [dummy_memo]
    mock_create.return_value = dummy_memo
    mock_update.return_value = dummy_memo

    res_list = runner.invoke(app, ["memo", "list"])
    assert res_list.exit_code == 0
    assert "FROTO" in res_list.stdout

    res_add = runner.invoke(app, ["memo", "add", "FROTO", "Not içeriği"])
    assert res_add.exit_code == 0
    assert "Memo added" in res_add.stdout

    res_up = runner.invoke(app, ["memo", "update", "42212", "Güncelleme"])
    assert res_up.exit_code == 0
    assert "Memo updated" in res_up.stdout

    res_del = runner.invoke(app, ["memo", "delete", "42212"])
    assert res_del.exit_code == 0
    assert "Memo deleted" in res_del.stdout


@patch("fintables.cli.commands.auth.login", new_callable=AsyncMock)
def test_cli_auth(mock_login):
    mock_login.return_value = ("access_token_1234567890", "refresh_token")
    result = runner.invoke(app, ["auth", "login", "-u", "myuser", "-p", "mypass"])
    assert result.exit_code == 0
    assert "Login successful" in result.stdout
