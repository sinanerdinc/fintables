import shlex
import sys
import typer
from rich.console import Console
from rich.prompt import Prompt

from fintables import __version__
from fintables.i18n import t

console = Console()


def shell_command() -> None:
    """Starts an interactive Fintables REPL shell session."""
    # Circular import önlemek için main içindeki app'i yerel alıyoruz
    from fintables.cli.main import app

    console.print(
        f"[bold cyan]============================================================[/bold cyan]\n"
        f"🚀 [bold green]Fintables Interactive Shell[/bold green] [dim](v{__version__})[/dim]\n"
        f"Komutları doğrudan yazabilirsiniz (örn: [yellow]company ASELS[/yellow], [yellow]symbol FROTO[/yellow]).\n"
        f"Çıkış için [bold red]exit[/bold red] veya [bold red]quit[/bold red], ekranı temizlemek için [bold yellow]clear[/bold yellow] yazın.\n"
        f"[bold cyan]============================================================[/bold cyan]\n"
    )

    while True:
        try:
            user_input = Prompt.ask("[bold green]fintables[/bold green]").strip()
        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]Görüşmek üzere![/dim]")
            break

        if not user_input:
            continue

        if user_input.lower() in ("exit", "quit", "q", ":q"):
            console.print("[bold cyan]Oturum kapatıldı.[/bold cyan]")
            break

        if user_input.lower() in ("clear", "cls"):
            console.clear()
            continue

        try:
            args = shlex.split(user_input)
            # Typer app'i komut satırı argümanları ile çağırıyoruz
            app(args=args, standalone_mode=False)
        except SystemExit:
            # Typer'ın sys.exit çağrısını yakalayarak shell oturumunun kapanmasını önlüyoruz
            pass
        except Exception as e:
            console.print(f"{t('error.prefix')} {e}")
