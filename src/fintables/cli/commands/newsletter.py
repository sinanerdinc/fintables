import asyncio
from typing import Optional
import typer
from rich.console import Console

from fintables.api.client import FintablesClient
from fintables.api.endpoints.newsletter import get_newsletter, list_newsletters
from fintables.exceptions import FintablesError
from fintables.i18n import t
from fintables.output.formatter import (
    print_json,
    print_newsletter_detail,
    print_newsletter_list,
)

console = Console()
newsletter_app = typer.Typer(help=t("cli.cmd.newsletter"))


@newsletter_app.command("list", help=t("cli.newsletter.list_help"))
def newsletter_list(
    main_category: str = typer.Option(
        "bist", "--category", "-c",
        help=t("cli.newsletter.category_help"),
    ),
    filter_title: Optional[str] = typer.Option(
        None, "--filter", "-f",
        help=t("cli.video.filter_help"),
    ),
    page_size: int = typer.Option(
        100, "--page-size",
        help=t("cli.feed.page_size_help"),
    ),
    page: Optional[int] = typer.Option(
        None, "--page",
        help=t("cli.newsletter.page_help"),
    ),
    output: str = typer.Option(
        "table", "--output", "-o",
        help=t("cli.common.output_help"),
    ),
) -> None:
    """Lists newsletters."""
    async def _run() -> None:
        async with FintablesClient() as client:
            try:
                result = await list_newsletters(
                    client,
                    main_category=main_category,
                    page_size=page_size,
                    page=page,
                )
                if output.lower() == "json":
                    print_json(result)
                else:
                    print_newsletter_list(result, category_filter=filter_title)
            except FintablesError as e:
                console.print(f"{t('error.prefix')} {e}")
                raise typer.Exit(code=1)
    asyncio.run(_run())


@newsletter_app.command("read", help=t("cli.newsletter.read_help"))
def newsletter_read(
    slug: str = typer.Argument(..., help=t("cli.newsletter.slug_help")),
    output: str = typer.Option(
        "table", "--output", "-o",
        help=t("cli.common.output_help"),
    ),
) -> None:
    """Reads newsletter content."""
    async def _run() -> None:
        async with FintablesClient() as client:
            try:
                detail = await get_newsletter(client, slug)
                if output.lower() == "json":
                    print_json(detail)
                else:
                    print_newsletter_detail(detail)
            except FintablesError as e:
                console.print(f"{t('error.prefix')} {e}")
                raise typer.Exit(code=1)
    asyncio.run(_run())
