import asyncio
from typing import Optional
import typer
from rich.console import Console

from fintables.api.client import FintablesClient
from fintables.api.endpoints.agenda import get_agenda
from fintables.exceptions import FintablesError
from fintables.i18n import t
from fintables.output.formatter import print_agenda_table, print_json

console = Console()

_TIME_CHOICES = ["today", "thisWeek", "nextWeek"]


def agenda_command(
    time: str = typer.Argument(
        "today",
        help=t("cli.agenda.time_help"),
    ),
    type_filter: Optional[str] = typer.Option(
        None, "--type", "-t",
        help=t("cli.agenda.type_help"),
    ),
    output: str = typer.Option(
        "table", "--output", "-o",
        help=t("cli.common.output_help"),
    ),
) -> None:
    """Fetches economic calendar and dividend agenda."""
    if time not in _TIME_CHOICES:
        console.print(
            f"{t('error.prefix')} {t('cli.agenda.invalid_time', time=time, options=', '.join(_TIME_CHOICES))}"
        )
        raise typer.Exit(code=1)

    async def _run() -> None:
        async with FintablesClient() as client:
            try:
                items = await get_agenda(client, time)  # type: ignore[arg-type]

                if type_filter:
                    items = [i for i in items if (i.type or "").lower() == type_filter.lower()]

                if output.lower() == "json":
                    print_json(items)
                else:
                    print_agenda_table(items, time)
            except FintablesError as e:
                console.print(f"{t('error.prefix')} {e}")
                raise typer.Exit(code=1)

    asyncio.run(_run())
