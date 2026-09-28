import asyncio
import typer
from rich.console import Console

from fintables.api.client import FintablesClient
from fintables.api.endpoints.search import search
from fintables.exceptions import FintablesError
from fintables.i18n import t
from fintables.output.formatter import print_json, print_search_results

console = Console()


def search_command(
    query: str = typer.Argument(..., help=t("cli.search.query_help")),
    output: str = typer.Option("table", "--output", "-o", help=t("cli.common.output_help")),
) -> None:
    """Searches stocks, futures, and warrants."""
    async def _run() -> None:
        async with FintablesClient() as client:
            try:
                res = await search(client, query)
                if output.lower() == "json":
                    print_json(res)
                else:
                    print_search_results(res, query)
            except FintablesError as e:
                console.print(f"{t('error.prefix')} {e}")
                raise typer.Exit(code=1)

    asyncio.run(_run())
