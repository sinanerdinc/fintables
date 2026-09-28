import asyncio
import typer
from rich.console import Console

from fintables.api.client import FintablesClient
from fintables.api.endpoints.companies import get_company
from fintables.exceptions import FintablesError
from fintables.i18n import t
from fintables.output.formatter import print_company_table, print_json

from fintables.cli.completion import complete_ticker

console = Console()


def company_command(
    ticker: str = typer.Argument(..., help=t("cli.common.ticker_help"), autocompletion=complete_ticker),
    output: str = typer.Option("table", "--output", "-o", help=t("cli.common.output_help")),
) -> None:
    """Fetches company general profile and ratio types."""
    async def _run() -> None:
        async with FintablesClient() as client:
            try:
                comp = await get_company(client, ticker)
                if output.lower() == "json":
                    print_json(comp)
                else:
                    print_company_table(comp)
            except FintablesError as e:
                console.print(f"{t('error.prefix')} {e}")
                raise typer.Exit(code=1)

    asyncio.run(_run())
