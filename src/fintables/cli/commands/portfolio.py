import asyncio
import re
import typer
from rich.console import Console
from rich.table import Table
from rich.box import ROUNDED

from fintables.api.client import FintablesClient
from fintables.api.endpoints.portfolio import (
    add_transaction,
    create_portfolio,
    delete_portfolio,
    get_positions,
    list_portfolios,
    update_portfolio,
)
from fintables.exceptions import FintablesError
from fintables.i18n import t
from fintables.output.formatter import print_json

console = Console()
portfolio_app = typer.Typer(help=t("cli.cmd.portfolio"))

_UUID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
    re.IGNORECASE,
)


# ── name -> id resolver ───────────────────────────────────────────────────────

async def _resolve(client: FintablesClient, name_or_id: str) -> tuple[str, str]:
    """Returns (id, title).

    UUID ise direkt kullanılır; değilse portföy listesi çekilip isim eşleşmesi
    yapılır (büyük/küçük harf duyarsız). Eşleşme yoksa veya belirsizse Exit.
    """
    if _UUID_RE.match(name_or_id):
        page = await list_portfolios(client)
        for p in page.results:
            if p.id == name_or_id:
                return p.id, p.title
        return name_or_id, name_or_id

    page = await list_portfolios(client)
    matches = [p for p in page.results if p.title.lower() == name_or_id.lower()]

    if not matches:
        names = ", ".join(f'"{p.title}"' for p in page.results) or "(no portfolios)"
        console.print(
            f"{t('error.prefix')} {t('cli.portfolio.not_found', identifier=name_or_id)}\n"
            f"{t('cli.portfolio.available_portfolios', names=names)}"
        )
        raise typer.Exit(code=1)

    if len(matches) > 1:
        ids = ", ".join(p.id for p in matches)
        console.print(
            f"{t('error.prefix')} {t('cli.portfolio.multiple_found', identifier=name_or_id)}\n"
            f"{t('cli.portfolio.use_uuid', ids=ids)}"
        )
        raise typer.Exit(code=1)

    return matches[0].id, matches[0].title


# ── list ──────────────────────────────────────────────────────────────────────

@portfolio_app.command("list", help=t("cli.portfolio.list_help"))
def portfolio_list(
    output: str = typer.Option("table", "--output", "-o", help=t("cli.common.output_help")),
) -> None:
    """Lists virtual portfolios."""
    async def _run() -> None:
        async with FintablesClient() as client:
            try:
                page = await list_portfolios(client)
                if output.lower() == "json":
                    print_json(page)
                else:
                    _print_portfolio_list(page)
            except FintablesError as e:
                console.print(f"{t('error.prefix')} {e}")
                raise typer.Exit(code=1)
    asyncio.run(_run())


# ── create ────────────────────────────────────────────────────────────────────

@portfolio_app.command("create", help=t("cli.portfolio.create_help"))
def portfolio_create(
    title: str = typer.Argument(..., help=t("cli.portfolio.create_title_help")),
    output: str = typer.Option("table", "--output", "-o", help=t("cli.common.output_help")),
) -> None:
    """Creates a new virtual portfolio."""
    async def _run() -> None:
        async with FintablesClient() as client:
            try:
                portfolio = await create_portfolio(client, title)
                if output.lower() == "json":
                    print_json(portfolio)
                else:
                    console.print(t("cli.portfolio.created", title=portfolio.title, id=portfolio.id))
            except FintablesError as e:
                console.print(f"{t('error.prefix')} {e}")
                raise typer.Exit(code=1)
    asyncio.run(_run())


# ── delete ────────────────────────────────────────────────────────────────────

@portfolio_app.command("delete", help=t("cli.portfolio.delete_help"))
def portfolio_delete(
    portfolio: str = typer.Argument(..., help=t("cli.portfolio.name_or_uuid_help")),
) -> None:
    """Deletes a virtual portfolio."""
    async def _run() -> None:
        async with FintablesClient() as client:
            try:
                pid, title = await _resolve(client, portfolio)
                await delete_portfolio(client, pid)
                console.print(t("cli.portfolio.deleted", identifier=f"{title} ({pid})"))
            except FintablesError as e:
                console.print(f"{t('error.prefix')} {e}")
                raise typer.Exit(code=1)
    asyncio.run(_run())


# ── rename ────────────────────────────────────────────────────────────────────

@portfolio_app.command("rename", help=t("cli.portfolio.rename_help"))
def portfolio_rename(
    portfolio: str = typer.Argument(..., help=t("cli.portfolio.name_or_uuid_help")),
    new_title: str = typer.Argument(..., help=t("cli.portfolio.rename_title_help")),
    output: str = typer.Option("table", "--output", "-o", help=t("cli.common.output_help")),
) -> None:
    """Renames a portfolio."""
    async def _run() -> None:
        async with FintablesClient() as client:
            try:
                pid, old_title = await _resolve(client, portfolio)
                updated = await update_portfolio(client, pid, new_title)
                if output.lower() == "json":
                    print_json(updated)
                else:
                    console.print(t("cli.portfolio.renamed", old_title=old_title, new_title=updated.title) + f" [dim]({pid})[/dim]")
            except FintablesError as e:
                console.print(f"{t('error.prefix')} {e}")
                raise typer.Exit(code=1)
    asyncio.run(_run())


# ── show ──────────────────────────────────────────────────────────────────────

@portfolio_app.command("show", help=t("cli.portfolio.show_help"))
def portfolio_show(
    portfolio: str = typer.Argument(..., help=t("cli.portfolio.name_or_uuid_help")),
    output: str = typer.Option("table", "--output", "-o", help=t("cli.common.output_help")),
) -> None:
    """Shows positions in a portfolio."""
    async def _run() -> None:
        async with FintablesClient() as client:
            try:
                pid, title = await _resolve(client, portfolio)
                page = await get_positions(client, pid)
                if output.lower() == "json":
                    print_json(page)
                else:
                    _print_positions(page, title)
            except FintablesError as e:
                console.print(f"{t('error.prefix')} {e}")
                raise typer.Exit(code=1)
    asyncio.run(_run())


# ── buy ───────────────────────────────────────────────────────────────────────

@portfolio_app.command("buy", help=t("cli.portfolio.buy_help"))
def portfolio_buy(
    portfolio: str = typer.Argument(..., help=t("cli.portfolio.name_or_uuid_help")),
    ticker: str = typer.Argument(..., help=t("cli.portfolio.ticker_help")),
    amount: float = typer.Argument(..., help=t("cli.portfolio.amount_help")),
    price: float = typer.Argument(..., help=t("cli.portfolio.price_help")),
    date: str = typer.Option(..., "--date", "-d", help=t("cli.portfolio.date_help")),
    output: str = typer.Option("table", "--output", "-o", help=t("cli.common.output_help")),
) -> None:
    """Adds a buy transaction to a portfolio."""
    async def _run() -> None:
        async with FintablesClient() as client:
            try:
                pid, title = await _resolve(client, portfolio)
                tx = await add_transaction(client, pid, ticker, "BUY", amount, price, date)
                if output.lower() == "json":
                    print_json(tx)
                else:
                    console.print(t("cli.portfolio.buy_success", portfolio=title, ticker=ticker.upper(), amount=f"{amount:,.0f}", price=price) + f" [dim]({date})[/dim]")
            except FintablesError as e:
                console.print(f"{t('error.prefix')} {e}")
                raise typer.Exit(code=1)
    asyncio.run(_run())


# ── sell ──────────────────────────────────────────────────────────────────────

@portfolio_app.command("sell", help=t("cli.portfolio.sell_help"))
def portfolio_sell(
    portfolio: str = typer.Argument(..., help=t("cli.portfolio.name_or_uuid_help")),
    ticker: str = typer.Argument(..., help=t("cli.portfolio.ticker_help")),
    amount: float = typer.Argument(..., help=t("cli.portfolio.amount_help")),
    price: float = typer.Argument(..., help=t("cli.portfolio.sell_price_help")),
    date: str = typer.Option(..., "--date", "-d", help=t("cli.portfolio.date_help")),
    output: str = typer.Option("table", "--output", "-o", help=t("cli.common.output_help")),
) -> None:
    """Adds a sell transaction to a portfolio."""
    async def _run() -> None:
        async with FintablesClient() as client:
            try:
                pid, title = await _resolve(client, portfolio)
                tx = await add_transaction(client, pid, ticker, "SELL", amount, price, date)
                if output.lower() == "json":
                    print_json(tx)
                else:
                    console.print(t("cli.portfolio.sell_success", portfolio=title, ticker=ticker.upper(), amount=f"{amount:,.0f}", price=price) + f" [dim]({date})[/dim]")
            except FintablesError as e:
                console.print(f"{t('error.prefix')} {e}")
                raise typer.Exit(code=1)
    asyncio.run(_run())


# ── internal printers ─────────────────────────────────────────────────────────

def _print_portfolio_list(page) -> None:
    if not page.results:
        console.print(f"[dim]{t('cli.portfolio.empty')}[/dim]")
        return
    table = Table(title=t("cli.portfolio.table_title"), box=ROUNDED)
    table.add_column(t("cli.portfolio.col_title"), style="bold cyan")
    table.add_column(t("cli.portfolio.col_id"), style="dim", no_wrap=True)
    for p in page.results:
        table.add_row(p.title, p.id)
    console.print(table)


def _print_positions(page, title: str) -> None:
    if not page.results:
        console.print(f"[dim]{t('cli.portfolio.positions_empty', title=title)}[/dim]")
        return

    table = Table(title=f"{t('cli.portfolio.pos_title', title=title)}", box=ROUNDED)
    table.add_column(t("cli.portfolio.col_stock"), style="bold cyan", no_wrap=True)
    table.add_column(t("cli.portfolio.col_quantity"), justify="right")
    table.add_column(t("cli.portfolio.col_avg_cost"), justify="right", style="dim")
    table.add_column(t("cli.portfolio.col_current_price"), justify="right", style="yellow")
    table.add_column(t("cli.portfolio.col_total_cost"), justify="right")
    table.add_column(t("cli.portfolio.col_total_value"), justify="right", style="bold yellow")
    table.add_column(t("cli.portfolio.col_gain_loss"), justify="right")
    table.add_column(t("cli.portfolio.col_gain_loss_pct"), justify="right")

    for pos in page.results:
        gain = pos.gain
        gain_pct = pos.gain_pct

        if gain is not None:
            color = "green" if gain >= 0 else "red"
            sign = "+" if gain >= 0 else ""
            gain_str = f"[{color}]{sign}{gain:,.2f}[/{color}]"
        else:
            gain_str = "[dim]--[/dim]"

        if gain_pct is not None:
            color = "green" if gain_pct >= 0 else "red"
            sign = "+" if gain_pct >= 0 else ""
            pct_str = f"[{color}]{sign}{gain_pct:.2f}%[/{color}]"
        else:
            pct_str = "[dim]--[/dim]"

        table.add_row(
            pos.code,
            f"{pos.amount:,.0f}" if pos.amount is not None else "--",
            f"{pos.avg_cost:,.4f}" if pos.avg_cost is not None else "--",
            f"{pos.current_price:,.4f}" if pos.current_price is not None else "--",
            f"{pos.total_cost:,.2f}" if pos.total_cost is not None else "--",
            f"{pos.total_value:,.2f}" if pos.total_value is not None else "--",
            gain_str,
            pct_str,
        )

    console.print(table)
