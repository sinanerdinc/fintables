import asyncio
import typer
from rich.console import Console

from fintables.api.auth import login
from fintables.api.client import FintablesClient
from fintables.config import settings
from fintables.exceptions import AuthError
from fintables.i18n import t

console = Console()
auth_app = typer.Typer(help=t("cli.cmd.auth"))


@auth_app.command("login", help=t("cli.auth.login_help"))
def auth_login(
    email: str = typer.Option(None, "--email", "-e", help=t("cli.auth.email_help")),
    username: str = typer.Option(None, "--username", "-u", help=t("cli.auth.username_help")),
    password: str = typer.Option(None, "--password", "-p", help=t("cli.auth.password_help")),
) -> None:
    """Logs in with email and password to test connection."""
    u = email or username or settings.email_or_username
    p = password or settings.password

    if not u or not p:
        console.print(
            f"{t('error.prefix')} {t('cli.auth.missing_credentials')}"
        )
        raise typer.Exit(code=1)

    async def _run() -> None:
        async with FintablesClient() as client:
            try:
                access, refresh = await login(
                    client._client,
                    u,
                    p,
                    base_url=settings.base_url,
                    headers=settings.default_headers,
                )
                console.print(f"[bold green]{t('cli.auth.login_success')}[/bold green]")
                console.print(t("cli.auth.access_token", token=access[:8]))
            except AuthError as e:
                console.print(f"{t('error.prefix')} {e}")
                raise typer.Exit(code=1)

    asyncio.run(_run())
