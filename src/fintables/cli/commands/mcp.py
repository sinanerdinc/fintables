import typer
from rich.console import Console

console = Console()


def mcp_command(
    transport: str = typer.Option("stdio", "--transport", "-t", help="Transport protocol: stdio or sse"),
) -> None:
    """Starts the Model Context Protocol (MCP) server for AI assistants (Claude, Cursor, Antigravity)."""
    from fintables.mcp.server import mcp

    if transport.lower() == "stdio":
        # Standard input/output transport for AI clients
        mcp.run(transport="stdio", show_banner=False)
    elif transport.lower() == "sse":
        # Server-Sent Events transport
        mcp.run(transport="sse", show_banner=False)
    else:
        console.print(f"[bold red]Hata:[/bold red] Desteklenmeyen transport protokolu: '{transport}'. (stdio veya sse olmalı)")
        raise typer.Exit(code=1)
