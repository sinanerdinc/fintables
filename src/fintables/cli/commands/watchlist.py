import asyncio
import typer
from rich.console import Console

from fintables.api.client import FintablesClient
from fintables.api.endpoints.watchlist import add_favorite, remove_favorite
from fintables.exceptions import FintablesError
from fintables.i18n import t
from fintables.output.formatter import print_json, print_watchlist

console = Console()
watchlist_app = typer.Typer(help=t("cli.cmd.watchlist"))


@watchlist_app.command("add", help=t("cli.watchlist.add_help"))
def watchlist_add(
    ticker: str = typer.Argument(..., help=t("cli.common.ticker_help")),
    output: str = typer.Option("table", "--output", "-o", help=t("cli.common.output_help")),
) -> None:
    """Adds a stock to favorites."""
    async def _run() -> None:
        async with FintablesClient() as client:
            try:
                res = await add_favorite(client, ticker)
                if output.lower() == "json":
                    print_json(res)
                else:
                    print_watchlist(res, action="add", ticker=ticker.upper())
            except FintablesError as e:
                console.print(f"{t('error.prefix')} {e}")
                raise typer.Exit(code=1)

    asyncio.run(_run())


@watchlist_app.command("remove", help=t("cli.watchlist.remove_help"))
def watchlist_remove(
    ticker: str = typer.Argument(..., help=t("cli.common.ticker_help")),
    output: str = typer.Option("table", "--output", "-o", help=t("cli.common.output_help")),
) -> None:
    """Removes a stock from favorites."""
    async def _run() -> None:
        async with FintablesClient() as client:
            try:
                res = await remove_favorite(client, ticker)
                if output.lower() == "json":
                    print_json(res)
                else:
                    print_watchlist(res, action="remove", ticker=ticker.upper())
            except FintablesError as e:
                console.print(f"{t('error.prefix')} {e}")
                raise typer.Exit(code=1)

    asyncio.run(_run())
