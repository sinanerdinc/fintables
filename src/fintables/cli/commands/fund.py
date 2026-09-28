import asyncio
import typer
from rich.console import Console

from fintables.api.client import FintablesClient
from fintables.api.endpoints.funds import get_fund, get_fund_info
from fintables.exceptions import FintablesError
from fintables.i18n import t
from fintables.output.formatter import print_json, print_fund_summary

console = Console()


def fund_command(
    ticker: str = typer.Argument(..., help=t("cli.fund.ticker_help")),
    output: str = typer.Option("table", "--output", "-o", help=t("cli.common.output_help")),
) -> None:
    """Fetches fund summary, asset allocation, and portfolio."""
    async def _run() -> None:
        async with FintablesClient() as client:
            try:
                fund = await get_fund(client, ticker)
                fund_info = await get_fund_info(client, ticker)
                
                if output.lower() == "json":
                    import json
                    combined = {
                        "fund": fund.model_dump(by_alias=True, mode="json"),
                        "info": fund_info.model_dump(by_alias=True, mode="json"),
                    }
                    console.print_json(json.dumps(combined, ensure_ascii=False))
                else:
                    print_fund_summary(fund, fund_info)
            except FintablesError as e:
                console.print(f"{t('error.prefix')} {e}")
                raise typer.Exit(code=1)

    asyncio.run(_run())
