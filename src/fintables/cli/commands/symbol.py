import asyncio
import typer
from rich.console import Console

from fintables.api.client import FintablesClient
from fintables.api.endpoints.sheets import get_sheets
from fintables.api.endpoints.symbols import get_symbol_summary
from fintables.exceptions import FintablesError
from fintables.i18n import t
from fintables.output.formatter import (
    print_json,
    print_sheets_table,
    print_symbol_summary_table,
)

from fintables.cli.completion import complete_ticker

console = Console()


def symbol_command(
    ticker: str = typer.Argument(..., help=t("cli.common.ticker_help"), autocompletion=complete_ticker),
    subcommand: str = typer.Argument("summary", help=t("cli.symbol.subcommand_help")),
    sheet: str = typer.Option("all", "--sheet", "-s", help=t("cli.symbol.sheet_help")),
    periods: int = typer.Option(5, "--periods", "-p", help=t("cli.symbol.periods_help")),
    quarterly: bool = typer.Option(False, "--quarterly", "-q", help=t("cli.symbol.quarterly_help")),
    output: str = typer.Option("table", "--output", "-o", help=t("cli.common.output_help")),
) -> None:
    """Fetches symbol summary or complete financial statements (sheets)."""
    async def _run() -> None:
        async with FintablesClient() as client:
            try:
                sub = subcommand.lower().strip()
                if sub == "summary":
                    res = await get_symbol_summary(client, ticker)
                    if output.lower() == "json":
                        print_json(res)
                    else:
                        print_symbol_summary_table(res)
                elif sub == "sheets":
                    res_sheets = await get_sheets(client, ticker)
                    if output.lower() == "json":
                        print_json(res_sheets)
                    else:
                        print_sheets_table(
                            res_sheets,
                            ticker=ticker.upper(),
                            sheet_name=sheet,
                            periods=periods,
                            quarterly=quarterly,
                        )
                else:
                    console.print(f"{t('error.prefix')} {t('error.unknown_subcommand', subcommand=subcommand, supported='summary, sheets')}")
                    raise typer.Exit(code=1)
            except FintablesError as e:
                console.print(f"{t('error.prefix')} {e}")
                raise typer.Exit(code=1)

    asyncio.run(_run())
