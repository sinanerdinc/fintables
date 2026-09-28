import asyncio
from typing import Optional
import typer
from rich.console import Console

from fintables.api.client import FintablesClient
from fintables.api.endpoints.post import get_post, list_posts
from fintables.exceptions import FintablesError
from fintables.i18n import t
from fintables.output.formatter import print_json, print_post_detail, print_post_list

console = Console()
post_app = typer.Typer(help=t("cli.cmd.post"))


@post_app.command("list", help=t("cli.post.list_help"))
def post_list(
    main_category: str = typer.Option(
        "bist", "--category", "-c",
        help=t("cli.post.category_help"),
    ),
    filter_title: Optional[str] = typer.Option(
        None, "--filter", "-f",
        help=t("cli.video.filter_help"),
    ),
    page: Optional[int] = typer.Option(
        None, "--page",
        help=t("cli.post.page_help"),
    ),
    output: str = typer.Option(
        "table", "--output", "-o",
        help=t("cli.common.output_help"),
    ),
) -> None:
    """Lists research articles and company notes."""
    async def _run() -> None:
        async with FintablesClient() as client:
            try:
                result = await list_posts(client, main_category=main_category, page=page)
                if output.lower() == "json":
                    print_json(result)
                else:
                    print_post_list(result, category_filter=filter_title)
            except FintablesError as e:
                console.print(f"{t('error.prefix')} {e}")
                raise typer.Exit(code=1)
    asyncio.run(_run())


@post_app.command("read", help=t("cli.post.read_help"))
def post_read(
    slug: str = typer.Argument(..., help=t("cli.post.slug_help")),
    output: str = typer.Option(
        "table", "--output", "-o",
        help=t("cli.common.output_help"),
    ),
) -> None:
    """Reads article content (content + similar articles)."""
    async def _run() -> None:
        async with FintablesClient() as client:
            try:
                detail = await get_post(client, slug)
                if output.lower() == "json":
                    print_json(detail)
                else:
                    print_post_detail(detail)
            except FintablesError as e:
                console.print(f"{t('error.prefix')} {e}")
                raise typer.Exit(code=1)
    asyncio.run(_run())
