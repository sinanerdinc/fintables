import asyncio
import typer
from rich.console import Console

from fintables.api.client import FintablesClient
from fintables.api.endpoints.feed import get_feed, get_topic_feed
from fintables.exceptions import FintablesError
from fintables.i18n import t
from fintables.output.formatter import print_feed_table, print_json

console = Console()


def feed_command(
    ticker: str = typer.Argument(None, help=t("cli.feed.ticker_help")),
    type: str = typer.Option(None, "--type", "-t", help=t("cli.feed.type_help")),
    importance: str = typer.Option(None, "--importance", "-i", help=t("cli.feed.importance_help")),
    page_size: int = typer.Option(30, "--page-size", help=t("cli.feed.page_size_help")),
    output: str = typer.Option("table", "--output", "-o", help=t("cli.common.output_help")),
) -> None:
    """Fetches news feed (KAP disclosures, newsletters, analyses) for a stock or global feed."""
    async def _run() -> None:
        async with FintablesClient() as client:
            try:
                if ticker:
                    page = await get_feed(client, ticker, page_size=page_size)
                else:
                    page = await get_topic_feed(client, page_size=page_size)
                
                if output.lower() == "json":
                    print_json(page)
                else:
                    print_feed_table(
                        page,
                        ticker=ticker.upper() if ticker else None,
                        type_filter=type,
                        importance_filter=importance,
                    )
            except FintablesError as e:
                console.print(f"{t('error.prefix')} {e}")
                raise typer.Exit(code=1)

    asyncio.run(_run())
