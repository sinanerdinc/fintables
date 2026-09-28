import asyncio
import typer
from rich.console import Console

from fintables.api.client import FintablesClient
from fintables.api.endpoints.memo import (
    create_memo,
    delete_memo,
    list_memos,
    update_memo,
)
from fintables.exceptions import FintablesError
from fintables.i18n import t
from fintables.output.formatter import (
    print_json,
    print_memo_action,
    print_memos_table,
)

console = Console()
memo_app = typer.Typer(help=t("cli.cmd.memo"))


@memo_app.command("list", help=t("cli.memo.list_help"))
def memo_list(
    ticker: str = typer.Option(None, "--ticker", "-t", help=t("cli.common.ticker_help")),
    output: str = typer.Option("table", "--output", "-o", help=t("cli.common.output_help")),
) -> None:
    """Lists all saved memos."""
    async def _run() -> None:
        async with FintablesClient() as client:
            try:
                memos = await list_memos(client)
                if output.lower() == "json":
                    print_json(memos)
                else:
                    print_memos_table(memos, ticker_filter=ticker)
            except FintablesError as e:
                console.print(f"{t('error.prefix')} {e}")
                raise typer.Exit(code=1)

    asyncio.run(_run())


@memo_app.command("add", help=t("cli.memo.add_help"))
def memo_add(
    ticker: str = typer.Argument(..., help=t("cli.common.ticker_help")),
    content: str = typer.Argument(..., help=t("cli.memo.content_help")),
    output: str = typer.Option("table", "--output", "-o", help=t("cli.common.output_help")),
) -> None:
    """Adds a new memo to a stock."""
    async def _run() -> None:
        async with FintablesClient() as client:
            try:
                memo = await create_memo(client, ticker, content)
                if output.lower() == "json":
                    print_json(memo)
                else:
                    print_memo_action("add", memo.id, code=memo.code, content=memo.content)
            except FintablesError as e:
                console.print(f"{t('error.prefix')} {e}")
                raise typer.Exit(code=1)

    asyncio.run(_run())


@memo_app.command("update", help=t("cli.memo.update_help"))
def memo_update(
    memo_id: int = typer.Argument(..., help=t("cli.memo.id_help")),
    content: str = typer.Argument(..., help=t("cli.memo.content_help")),
    ticker: str = typer.Option("", "--code", "-c", help=t("cli.memo.code_help")),
    output: str = typer.Option("table", "--output", "-o", help=t("cli.common.output_help")),
) -> None:
    """Updates an existing memo."""
    async def _run() -> None:
        async with FintablesClient() as client:
            try:
                # If ticker is empty, fetch existing memo to keep its code
                code = ticker
                if not code:
                    all_memos = await list_memos(client)
                    target = next((m for m in all_memos if m.id == memo_id), None)
                    if target:
                        code = target.code
                    else:
                        code = "SYMBOL"

                memo = await update_memo(client, memo_id, code, content)
                if output.lower() == "json":
                    print_json(memo)
                else:
                    print_memo_action("update", memo.id, code=memo.code, content=memo.content)
            except FintablesError as e:
                console.print(f"{t('error.prefix')} {e}")
                raise typer.Exit(code=1)

    asyncio.run(_run())


@memo_app.command("delete", help=t("cli.memo.delete_help"))
def memo_delete(
    memo_id: int = typer.Argument(..., help=t("cli.memo.id_help")),
    output: str = typer.Option("table", "--output", "-o", help=t("cli.common.output_help")),
) -> None:
    """Deletes a memo."""
    async def _run() -> None:
        async with FintablesClient() as client:
            try:
                await delete_memo(client, memo_id)
                if output.lower() == "json":
                    print_json({"deleted": True, "id": memo_id})
                else:
                    print_memo_action("delete", memo_id)
            except FintablesError as e:
                console.print(f"{t('error.prefix')} {e}")
                raise typer.Exit(code=1)

    asyncio.run(_run())
