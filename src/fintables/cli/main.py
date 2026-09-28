import typer

from fintables import __version__
from fintables.i18n import t, set_language, register_i18n, sync_cli_translations
from fintables.cli.commands.analyst import analyst_command
from fintables.cli.commands.agenda import agenda_command
from fintables.cli.commands.auth import auth_app
from fintables.cli.commands.company import company_command
from fintables.cli.commands.feed import feed_command
from fintables.cli.commands.fund import fund_command
from fintables.cli.commands.memo import memo_app
from fintables.cli.commands.search import search_command
from fintables.cli.commands.symbol import symbol_command
from fintables.cli.commands.watchlist import watchlist_app
from fintables.cli.commands.portfolio import portfolio_app
from fintables.cli.commands.newsletter import newsletter_app
from fintables.cli.commands.post import post_app
from fintables.cli.commands.shell import shell_command
from fintables.cli.commands.video import video_app
from fintables.cli.commands.notification import notification_app

app = typer.Typer(
    name="fintables",
    help=t("cli.app.help"),
    no_args_is_help=True,
)
register_i18n(app, "cli.app.help")


def version_callback(value: bool) -> None:
    if value:
        typer.echo(f"fintables version: {__version__}")
        raise typer.Exit()


@app.callback()
def main_callback(
    version: bool = typer.Option(
        None,
        "--version",
        "-v",
        help=t("cli.app.version_help"),
        callback=version_callback,
        is_eager=True,
    ),
    lang: str = typer.Option(
        None,
        "--lang",
        "-l",
        help=t("cli.app.lang_help"),
        is_eager=True,
    ),
) -> None:
    if lang:
        set_language(lang)


# Register top-level commands
cmd_company = app.command(name="company", help=t("cli.cmd.company"))(company_command)
register_i18n(cmd_company, "cli.cmd.company")

cmd_symbol = app.command(name="symbol", help=t("cli.cmd.symbol"))(symbol_command)
register_i18n(cmd_symbol, "cli.cmd.symbol")

cmd_analyst = app.command(name="analyst", help=t("cli.cmd.analyst"))(analyst_command)
register_i18n(cmd_analyst, "cli.cmd.analyst")

cmd_search = app.command(name="search", help=t("cli.cmd.search"))(search_command)
register_i18n(cmd_search, "cli.cmd.search")

cmd_feed = app.command(name="feed", help=t("cli.cmd.feed"))(feed_command)
register_i18n(cmd_feed, "cli.cmd.feed")

cmd_fund = app.command(name="fund", help=t("cli.cmd.fund"))(fund_command)
register_i18n(cmd_fund, "cli.cmd.fund")

cmd_agenda = app.command(name="agenda", help=t("cli.cmd.agenda"))(agenda_command)
register_i18n(cmd_agenda, "cli.cmd.agenda")

cmd_shell = app.command(name="shell", help=t("cli.cmd.shell"))(shell_command)
register_i18n(cmd_shell, "cli.cmd.shell")

# Register command groups
app.add_typer(watchlist_app, name="watchlist")
register_i18n(watchlist_app, "cli.cmd.watchlist")

app.add_typer(memo_app, name="memo")
register_i18n(memo_app, "cli.cmd.memo")

app.add_typer(auth_app, name="auth")
register_i18n(auth_app, "cli.cmd.auth")

app.add_typer(portfolio_app, name="portfolio")
register_i18n(portfolio_app, "cli.cmd.portfolio")

app.add_typer(newsletter_app, name="newsletter")
register_i18n(newsletter_app, "cli.cmd.newsletter")

app.add_typer(post_app, name="post")
register_i18n(post_app, "cli.cmd.post")

app.add_typer(video_app, name="video")
register_i18n(video_app, "cli.cmd.video")

app.add_typer(notification_app, name="notification")
register_i18n(notification_app, "cli.cmd.notification")

sync_cli_translations()


def main() -> None:
    app()


if __name__ == "__main__":
    main()
