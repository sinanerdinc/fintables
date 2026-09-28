"""CLI Autocompletion helpers for Typer shell integration."""

POPULAR_TICKERS = [
    "AKBNK", "ALARK", "ARCLK", "ASELS", "BIMAS", "EKGYO", "ENKAI", "EREGL",
    "FROTO", "GARAN", "HEKTS", "ISCTR", "KCHOL", "KONTR", "KOZAL", "KRDMD",
    "ODAS", "PETKM", "PGSUS", "SAHOL", "SASA", "SISE", "TCELL", "THYAO",
    "TOASO", "TUPRS", "VAKBN", "YKBNK"
]


def complete_ticker(incomplete: str):
    """Provides autocomplete suggestions for stock tickers in terminal."""
    incomplete_upper = incomplete.upper()
    for ticker in POPULAR_TICKERS:
        if ticker.startswith(incomplete_upper):
            yield ticker
