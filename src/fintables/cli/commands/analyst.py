import asyncio
import typer
from rich.console import Console

from fintables.api.client import FintablesClient
from fintables.api.endpoints.analyst_ratings import get_analyst_ratings
from fintables.exceptions import FintablesError
from fintables.i18n import t
from fintables.output.formatter import print_analyst_ratings_table, print_json

console = Console()


def analyst_command(
    ticker: str = typer.Argument(..., help=t("cli.common.ticker_help")),
    brokerage: str = typer.Option(None, "--brokerage", "-b", help=t("cli.analyst.brokerage_help")),
    model_portfolio: bool = typer.Option(False, "--model-portfolio", "-m", help=t("cli.analyst.model_portfolio_help")),
    output: str = typer.Option("table", "--output", "-o", help=t("cli.common.output_help")),
) -> None:
    """Fetches analyst forecasts and target prices from brokerages."""
    async def _run() -> None:
        async with FintablesClient() as client:
            try:
                ratings = await get_analyst_ratings(
                    client,
                    ticker,
                    brokerage_id=brokerage,
                    in_model_portfolio=True if model_portfolio else None,
                )
                if output.lower() == "json":
                    print_json(ratings)
                else:
                    print_analyst_ratings_table(
                        ratings,
                        ticker=ticker.upper(),
                        brokerage_filter=brokerage,
                        model_portfolio_only=model_portfolio,
                    )
            except FintablesError as e:
                console.print(f"{t('error.prefix')} {e}")
                raise typer.Exit(code=1)

    asyncio.run(_run())
