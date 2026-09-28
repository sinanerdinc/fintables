import asyncio
import typer
from rich.console import Console

from fintables.api.client import FintablesClient
from fintables.api.endpoints.notifications import (
    get_unread_status,
    list_notifications,
    mark_notifications_as_read,
)
from fintables.exceptions import FintablesError
from fintables.i18n import t
from fintables.output.formatter import (
    print_json,
    print_notification_action,
    print_notification_status,
    print_notifications_table,
)

console = Console()
notification_app = typer.Typer(help=t("cli.cmd.notification"))


@notification_app.command("list", help=t("cli.notification.list_help"))
def notification_list(
    page_size: int = typer.Option(100, "--page-size", "-p", help=t("cli.notification.page_size_help")),
    output: str = typer.Option("table", "--output", "-o", help=t("cli.common.output_help")),
) -> None:
    """Lists notifications."""
    async def _run() -> None:
        async with FintablesClient() as client:
            try:
                page = await list_notifications(client, page_size=page_size)
                if output.lower() == "json":
                    print_json(page)
                else:
                    print_notifications_table(page)
            except FintablesError as e:
                console.print(f"{t('error.prefix')} {e}")
                raise typer.Exit(code=1)

    asyncio.run(_run())


@notification_app.command("unread", help=t("cli.notification.unread_help"))
def notification_unread(
    output: str = typer.Option("table", "--output", "-o", help=t("cli.common.output_help")),
) -> None:
    """Displays unread notification status and last read timestamp."""
    async def _run() -> None:
        async with FintablesClient() as client:
            try:
                status = await get_unread_status(client)
                if output.lower() == "json":
                    print_json(status)
                else:
                    print_notification_status(status)
            except FintablesError as e:
                console.print(f"{t('error.prefix')} {e}")
                raise typer.Exit(code=1)

    asyncio.run(_run())


@notification_app.command("status", help=t("cli.notification.status_help"))
def notification_status(
    output: str = typer.Option("table", "--output", "-o", help=t("cli.common.output_help")),
) -> None:
    """Displays unread notification status and last read timestamp (alias for unread)."""
    notification_unread(output=output)


@notification_app.command("mark-read", help=t("cli.notification.mark_read_help"))
def notification_mark_read(
    output: str = typer.Option("table", "--output", "-o", help=t("cli.common.output_help")),
) -> None:
    """Marks all notifications as read."""
    async def _run() -> None:
        async with FintablesClient() as client:
            try:
                resp = await mark_notifications_as_read(client)
                if output.lower() == "json":
                    print_json(resp)
                else:
                    print_notification_action(action="mark_read", status=resp.status)
            except FintablesError as e:
                console.print(f"{t('error.prefix')} {e}")
                raise typer.Exit(code=1)

    asyncio.run(_run())
