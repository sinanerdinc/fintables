import asyncio
from typing import Optional
import typer
from rich.console import Console

from fintables.api.client import FintablesClient
from fintables.api.endpoints.video import get_video, list_videos
from fintables.exceptions import FintablesError
from fintables.i18n import t
from fintables.output.formatter import print_json, print_video_detail, print_video_list

console = Console()
video_app = typer.Typer(help=t("cli.cmd.video"))


@video_app.command("list", help=t("cli.video.list_help"))
def video_list(
    main_category: str = typer.Option(
        "bist", "--category", "-c",
        help=t("cli.newsletter.category_help"),
    ),
    type_: str = typer.Option(
        "video", "--type", "-t",
        help=t("cli.video.type_help"),
    ),
    series: Optional[str] = typer.Option(
        None, "--series", "-s",
        help=t("cli.video.series_help"),
    ),
    filter_text: Optional[str] = typer.Option(
        None, "--filter", "-f",
        help=t("cli.video.filter_help"),
    ),
    page: Optional[int] = typer.Option(
        None, "--page",
        help=t("cli.video.page_help"),
    ),
    output: str = typer.Option(
        "table", "--output", "-o",
        help=t("cli.common.output_help"),
    ),
) -> None:
    """Lists videos."""
    async def _run() -> None:
        async with FintablesClient() as client:
            try:
                result = await list_videos(
                    client,
                    type_=type_,
                    main_category=main_category,
                    page=page,
                )
                if output.lower() == "json":
                    print_json(result)
                else:
                    print_video_list(result, filter_query=filter_text, series_filter=series)
            except FintablesError as e:
                console.print(f"{t('error.prefix')} {e}")
                raise typer.Exit(code=1)
    asyncio.run(_run())


@video_app.command("show", help=t("cli.video.show_help"))
def video_show(
    slug: str = typer.Argument(..., help=t("cli.video.slug_help")),
    output: str = typer.Option(
        "table", "--output", "-o",
        help=t("cli.common.output_help"),
    ),
) -> None:
    """Shows video details, description, and YouTube link."""
    async def _run() -> None:
        async with FintablesClient() as client:
            try:
                detail = await get_video(client, slug)
                if output.lower() == "json":
                    print_json(detail)
                else:
                    print_video_detail(detail)
            except FintablesError as e:
                console.print(f"{t('error.prefix')} {e}")
                raise typer.Exit(code=1)
    asyncio.run(_run())
