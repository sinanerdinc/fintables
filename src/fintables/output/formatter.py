import re
from datetime import datetime
from typing import Any
from pydantic import BaseModel
from rich import print as rprint
from rich.box import ROUNDED
from rich.console import Console
from rich.markup import escape
from rich.panel import Panel
from rich.table import Table

from fintables.models.analyst_rating import AnalystRatingList, RatingType
from fintables.models.company import Company
from fintables.models.feed import FeedPage, NewsItem, PostItem
from fintables.models.memo import Memo
from fintables.models.search import SearchResponse
from fintables.models.sheets import Sheet, Sheets
from fintables.models.symbol import DataItem, SymbolSummary
from fintables.models.watchlist import WatchlistResponse
from fintables.models.fund import Fund, FundInfo
from fintables.models.agenda import AgendaItem
from fintables.models.newsletter import NewsletterListItem, NewsletterDetail, EditorBlock
from fintables.models.post import PostDetail, PostListItem
from fintables.models.video import VideoItem, VideoPage
from fintables.models.notification import (
    MarkAsReadResponse,
    NotificationPage,
    NotificationUnreadStatus,
)
from fintables.i18n import t, t_term

console = Console()


def abbreviate_number(val: float | int | None, decimals: int = 2) -> str:
    """Abbreviates large numbers to K, M, B, T format."""
    if val is None:
        return "—"
    num = float(val)
    sign = "-" if num < 0 else ""
    num = abs(num)

    if num >= 1e12:
        return f"{sign}{num / 1e12:.{decimals}f}T"
    elif num >= 1e9:
        return f"{sign}{num / 1e9:.{decimals}f}B"
    elif num >= 1e6:
        return f"{sign}{num / 1e6:.{decimals}f}M"
    elif num >= 1e3:
        return f"{sign}{num / 1e3:.{decimals}f}K"
    else:
        return f"{sign}{num:.{decimals}f}"


def format_data_item(item: DataItem) -> str:
    """Formats a DataItem according to its type and format specification."""
    if item.value is None:
        return "—" if item.format.null_to_na else ""

    item_type = item.type.lower()
    val = item.value

    try:
        if item_type in ("percentage", "percent"):
            fval = float(val)
            return f"{fval:.{item.format.decimals}f}%"
        elif item_type in ("currency", "number", "float"):
            fval = float(val)
            if item.format.abbreviation:
                return abbreviate_number(fval, item.format.decimals)
            return f"{fval:,.{item.format.decimals}f}"
        elif item_type in ("boolean", "bool"):
            bval = str(val).lower() in ("true", "1", "t", "yes", "uygun", "eligible")
            return t("common.yes") if bval else t("common.no")
        elif item_type in ("string", "str"):
            sval = str(val).strip()
            if sval.lower() in ("uygun değil", "not eligible"):
                return t("output.not_eligible")
            elif sval.lower() in ("uygun", "eligible"):
                return t("output.eligible")
            return t_term(sval)
    except (ValueError, TypeError):
        pass

    return str(val)


def _translate_json_data(obj: Any) -> Any:
    """Recursively translates title, label, and name fields for JSON output."""
    from fintables.i18n import t_term, get_language
    if get_language() == "tr":
        return obj

    if isinstance(obj, dict):
        new_obj = {}
        for k, v in obj.items():
            if isinstance(v, (dict, list)):
                new_obj[k] = _translate_json_data(v)
            elif isinstance(v, str) and k in ("title", "label", "name"):
                new_obj[k] = t_term(v)
            else:
                new_obj[k] = v
        return new_obj
    elif isinstance(obj, list):
        return [_translate_json_data(item) for item in obj]
    return obj


def print_json(data: Any) -> None:
    """Prints Pydantic model or dict as colored JSON, applying translations if needed."""
    import json
    
    if isinstance(data, BaseModel):
        dumped = data.model_dump(by_alias=True, mode="json")
    elif isinstance(data, list) and all(isinstance(x, BaseModel) for x in data):
        dumped = [x.model_dump(by_alias=True, mode="json") for x in data]
    elif isinstance(data, dict):
        dumped = data
    else:
        dumped = data

    dumped = _translate_json_data(dumped)
    console.print_json(json.dumps(dumped, default=str, ensure_ascii=False))


def print_company_table(company: Company) -> None:
    """Prints company header panel and ratio types table."""
    price_str = f"{company.price:.2f} TL" if company.price is not None else "—"
    enflasyon_str = "[bold green]✓[/bold green]" if company.enflasyon else "[bold red]✗[/bold red]"
    katilim_str = "[bold green]✓[/bold green]" if company.in_katilim_index else "[bold red]✗[/bold red]"

    panel_text = (
        f"[bold cyan]{escape(company.code)}[/bold cyan]  [bold white]{escape(company.title)}[/bold white]\n"
        f"{t('output.fund_price')} [yellow]{price_str}[/yellow]  │  "
        f"{t('output.inflation_accounting')}: {enflasyon_str}  │  "
        f"{t('output.participation_index')}: {katilim_str}"
    )
    if company.description:
        desc = (company.description[:250] + "...") if len(company.description) > 250 else company.description
        panel_text += f"\n\n[dim]{escape(desc)}[/dim]"

    console.print(Panel(panel_text, box=ROUNDED, border_style="cyan"))

    if company.ratio_types:
        console.print(f"\n[bold]{t('output.ratio_types')}[/bold]")
        table = Table(box=ROUNDED)
        table.add_column(t("output.col_category"), style="cyan", no_wrap=True)
        table.add_column(t("output.col_ratio"), style="white")
        table.add_column(t("output.col_access"), justify="center")

        for rt in company.ratio_types:
            first = True
            for item in rt.data:
                category_cell = t_term(rt.name) if first else ""
                first = False
                access_badge = "[green]✓[/green]" if item.allowed else "[red]✗[/red]"
                table.add_row(category_cell, t_term(item.name), access_badge)

        console.print(table)


def print_symbol_summary_table(summary: SymbolSummary) -> None:
    """Prints symbol summary tables: multipliers, details, income/balance statement, yield analysis."""
    data = summary.data

    # Multipliers
    if data.multipliers and data.multipliers.data:
        table_mul = Table(title=f"── {t_term(data.multipliers.title)} ──", box=ROUNDED, show_header=False)
        table_mul.add_column(t("output.col_item"), style="cyan")
        table_mul.add_column(t("output.col_value"), justify="right", style="bold yellow")
        for item in data.multipliers.data:
            table_mul.add_row(t_term(item.title), format_data_item(item))
        console.print(table_mul)

    # Company Details
    if data.company_details and data.company_details.data:
        table_det = Table(title=f"── {t_term(data.company_details.title)} ──", box=ROUNDED, show_header=False)
        table_det.add_column(t("output.col_item"), style="cyan")
        table_det.add_column(t("output.col_value"), justify="right", style="white")
        for item in data.company_details.data:
            table_det.add_row(t_term(item.title), format_data_item(item))
        console.print(table_det)

    # Income Statement Summary
    if data.income_statement and data.income_statement.data:
        p = data.income_statement.period
        period_str = f"({p.year}/{p.month:02d})"
        table_inc = Table(title=f"── {t_term(data.income_statement.title)} {period_str} ──", box=ROUNDED, show_header=False)
        table_inc.add_column(t("output.col_item"), style="cyan")
        table_inc.add_column(t("output.col_value"), justify="right", style="green")
        for item in data.income_statement.data:
            table_inc.add_row(t_term(item.title), format_data_item(item))
        console.print(table_inc)

    # Balance Statement Summary
    if data.balance_statement and data.balance_statement.data:
        p = data.balance_statement.period
        period_str = f"({p.year}/{p.month:02d})"
        table_bal = Table(title=f"── {t_term(data.balance_statement.title)} {period_str} ──", box=ROUNDED, show_header=False)
        table_bal.add_column(t("output.col_item"), style="cyan")
        table_bal.add_column(t("output.col_value"), justify="right", style="green")
        for item in data.balance_statement.data:
            table_bal.add_row(t_term(item.title), format_data_item(item))
        console.print(table_bal)

    # Yield Analysis
    if data.yield_ and data.yield_.data:
        table_yield = Table(title=f"── {t_term(data.yield_.title)} ──", box=ROUNDED)
        table_yield.add_column(t("output.col_period"), style="cyan", no_wrap=True)
        table_yield.add_column(t("output.col_initial"), justify="right")
        table_yield.add_column(t("output.col_low"), justify="right", style="red")
        table_yield.add_column(t("output.col_high"), justify="right", style="green")

        order = ["1w", "1m", "3m", "6m", "1y", "ytd"]
        all_keys = list(data.yield_.data.keys())
        keys = [k for k in order if k in all_keys] + [k for k in all_keys if k not in order]

        labels = {
            "1w": t("output.period_1w"),
            "1m": t("output.fund_1m"),
            "3m": t("output.fund_3m"),
            "6m": t("output.fund_6m"),
            "1y": t("output.fund_1y"),
            "ytd": t("output.fund_ytd"),
        }

        for k in keys:
            yw = data.yield_.data[k]
            f_str = f"{yw.first:.2f}" if yw.first is not None else "—"
            l_str = f"{yw.low:.2f}" if yw.low is not None else "—"
            h_str = f"{yw.high:.2f}" if yw.high is not None else "—"
            table_yield.add_row(labels.get(k, k.upper()), f_str, l_str, h_str)

        console.print(table_yield)


def rating_type_badge(val: RatingType | str | None) -> str:
    """Returns rich formatted badge string for analyst rating type."""
    if not val:
        return "[dim]—[/dim]"
    str_val = val.value if isinstance(val, RatingType) else str(val).lower()
    badges = {
        "al": f"[bold green]{t('output.badge_buy')}[/bold green]",
        "endeks_ustu": f"[bold cyan]{t('output.badge_outperform')}[/bold cyan]",
        "endekse_paralel": f"[bold yellow]{t('output.badge_market_perform')}[/bold yellow]",
        "tut": f"[bold yellow]{t('output.badge_hold')}[/bold yellow]",
        "sat": f"[bold red]{t('output.badge_sell')}[/bold red]",
        "endeks_alti": f"[bold red]{t('output.badge_underperform')}[/bold red]",
    }
    return badges.get(str_val, f"[white]{str_val.upper()}[/white]")


def print_analyst_ratings_table(
    ratings: AnalystRatingList,
    ticker: str,
    brokerage_filter: str | None = None,
    model_portfolio_only: bool = False,
) -> None:
    """Prints analyst ratings table with target prices and color-coded recommendations."""
    items = ratings.results
    if brokerage_filter:
        b_clean = brokerage_filter.strip().upper()
        items = [i for i in items if i.brokerage.code.upper() == b_clean or (i.brokerage.short_title and b_clean in i.brokerage.short_title.upper())]
    if model_portfolio_only:
        items = [i for i in items if i.in_model_portfolio]

    total_count = len(items)
    console.print(f"\n[bold]{t('output.analyst_ratings_header', ticker=ticker, count=total_count)}[/bold]")

    table = Table(box=ROUNDED)
    table.add_column(t("output.col_brokerage"), style="white")
    table.add_column(t("output.col_rating"), justify="center")
    table.add_column(t("output.col_target_price"), justify="right", style="bold yellow")
    table.add_column(t("output.col_portfolio"), justify="center", style="yellow")
    table.add_column(t("output.col_date"), justify="right", style="dim")

    counts: dict[str, int] = {}
    price_targets: list[float] = []

    for r in items:
        badge = rating_type_badge(r.type)
        r_str = r.type.value if isinstance(r.type, RatingType) else str(r.type or "")
        if r_str:
            counts[r_str] = counts.get(r_str, 0) + 1

        price_str = f"{r.price_target:.2f}" if r.price_target is not None else "—"
        if r.price_target is not None:
            price_targets.append(r.price_target)

        portfolio_icon = "★" if r.in_model_portfolio else ""
        date_str = r.published_at.strftime("%d %b %Y") if isinstance(r.published_at, datetime) else str(r.published_at)

        table.add_row(
            r.brokerage.short_title or r.brokerage.title,
            badge,
            price_str,
            portfolio_icon,
            date_str,
        )

    console.print(table)

    # Footer stats
    if price_targets:
        avg_target = sum(price_targets) / len(price_targets)
        stats = [t("output.avg_target", target=avg_target)]
        if "al" in counts:
            stats.append(f"{t('output.badge_buy')}: [bold green]{counts['al']}[/bold green]")
        if "endeks_ustu" in counts:
            stats.append(f"{t('output.badge_outperform')}: [bold cyan]{counts['endeks_ustu']}[/bold cyan]")
        if "tut" in counts:
            stats.append(f"{t('output.badge_hold')}: [bold yellow]{counts['tut']}[/bold yellow]")
        if "endekse_paralel" in counts:
            stats.append(f"{t('output.badge_market_perform')}: [bold yellow]{counts['endekse_paralel']}[/bold yellow]")
        if "sat" in counts:
            stats.append(f"{t('output.badge_sell')}: [bold red]{counts['sat']}[/bold red]")
        console.print("  │  ".join(stats))


def _render_sheet_table(sheet: Sheet, title: str, periods_count: int, quarterly: bool) -> None:
    display_periods = sheet.periods[:periods_count]
    mode_str = t("output.sheet_quarterly") if quarterly else t("output.sheet_cumulative")

    table = Table(title=f"{title} ({mode_str})", box=ROUNDED)
    table.add_column(t("output.col_item"), style="white")
    for p in display_periods:
        table.add_column(f"{p.year}/{p.month:02d}", justify="right")

    for row in sheet.rows:
        is_bold = row.level == 0
        indent = "" if is_bold else "  "
        t_label = t_term(row.label)
        label = f"[bold]{indent}{t_label}[/bold]" if is_bold else f"{indent}{t_label}"

        vals = row.quarter_values if quarterly else row.values
        vals_to_show = vals[:periods_count]

        formatted_vals = []
        for v in vals_to_show:
            if v is None:
                formatted_vals.append("[dim]—[/dim]")
            else:
                s = abbreviate_number(v, decimals=3)
                formatted_vals.append(f"[bold]{s}[/bold]" if is_bold else s)

        # Pad with dashes if fewer values than periods
        while len(formatted_vals) < len(display_periods):
            formatted_vals.append("[dim]—[/dim]")

        table.add_row(label, *formatted_vals)

    console.print(table)


def print_sheets_table(
    sheets: Sheets,
    ticker: str,
    sheet_name: str | None = None,
    periods: int = 5,
    quarterly: bool = False,
) -> None:
    """Prints financial sheets matrix (balance, income, cashflow)."""
    target = (sheet_name or "all").lower()

    if target in ("all", "balance"):
        _render_sheet_table(sheets.balance, f"{ticker} — {t('output.sheet_balance')}", periods, quarterly)
    if target in ("all", "income"):
        _render_sheet_table(sheets.income, f"{ticker} — {t('output.sheet_income')}", periods, quarterly)
    if target in ("all", "cashflow"):
        _render_sheet_table(sheets.cashflow, f"{ticker} — {t('output.sheet_cash_flow')}", periods, quarterly)

    console.print(f"[dim]{t('output.inflation_note')}[/dim]")


def print_feed_table(
    page: FeedPage,
    ticker: str | None = None,
    type_filter: str | None = None,
    importance_filter: str | None = None,
) -> None:
    """Prints news/feed items with icons and importance dots."""
    items = page.results
    if type_filter:
        items = [i for i in items if i.type.lower() == type_filter.lower()]
    if importance_filter:
        imp_clean = importance_filter.lower()
        items = [i for i in items if getattr(i, "importance", None) and str(getattr(i, "importance")).lower() == imp_clean]

    ticker_text = f"{ticker} — " if ticker else t("output.feed_general")
    console.print(f"\n[bold]{t('output.feed_header', ticker=ticker_text, count=len(items))}[/bold]")

    table = Table(box=ROUNDED)
    table.add_column(t("output.col_type"), justify="center", no_wrap=True)
    table.add_column(t("output.col_importance"), justify="center", no_wrap=True)
    if not ticker:
        table.add_column(t("output.col_company"), style="bold cyan", no_wrap=True)
    table.add_column(t("output.col_title"), style="white")
    table.add_column(t("output.col_date"), justify="right", style="dim", no_wrap=True)

    type_icons = {
        "post": "📰",
        "news": "📌",
        "newsletter": "📬",
        "article": "📜",
    }

    importance_badges = {
        "high": "[bold red]●●● HIGH[/bold red]",
        "mid": "[bold yellow]●○○ MID [/bold yellow]",
        "low": "[dim green]○○○ LOW [/dim green]",
    }

    for item in items:
        icon = type_icons.get(item.type, "📄")
        imp = getattr(item, "importance", None)
        imp_badge = importance_badges.get(str(imp).lower(), "[dim]—[/dim]") if imp else "[dim]—[/dim]"

        # Resolve company codes
        companies: list[str] = []
        if isinstance(item, NewsItem):
            companies = item.news.companies or [s.code for s in item.news.symbols]
        if not companies:
            companies = [str(t.id) for t in item.topics if t.type in ("symbol", "company") and t.id]
        company_str = ", ".join(dict.fromkeys(str(c) for c in companies)) if companies else "[dim]—[/dim]"

        title = escape(item.title)
        if item.type == "news" and isinstance(item, NewsItem):
            kap_type = escape(item.news.type or "")
            prefix = f"[KAP/{kap_type}] " if kap_type else "[KAP] "
            title = f"[cyan]{prefix}[/cyan]{title}"
            if item.news.note:
                title += f"\n[dim]{escape(item.news.note)}[/dim]"

        date_str = item.date.strftime("%d %b %Y %H:%M") if isinstance(item.date, datetime) else str(item.date)

        if not ticker:
            table.add_row(icon, imp_badge, company_str, title, date_str)
        else:
            table.add_row(icon, imp_badge, title, date_str)

    console.print(table)
    if page.next:
        console.print("[dim]ℹ️  Next page available. (Increase with --page-size)[/dim]")


def print_watchlist(resp: WatchlistResponse, action: str = "add", ticker: str = "") -> None:
    """Prints watchlist update confirmation."""
    items = resp.watchlist.items
    items_str = ", ".join(items) if items else t("output.watchlist_empty")

    if action == "add":
        console.print(f"[bold green]{t('output.watchlist_added', ticker=ticker)}[/bold green]")
    else:
        console.print(f"[bold yellow]{t('output.watchlist_removed', ticker=ticker)}[/bold yellow]")

    console.print(t("output.watchlist_label", items=f"[cyan]{items_str}[/cyan]"))


def print_search_results(resp: SearchResponse, query: str) -> None:
    """Prints multi-search results grouped by collection."""
    console.print(f'\n[bold]{t("output.search_header", query=query)}[/bold]\n')

    # Mapping groups by index / filter_by
    group_titles = [
        t("output.search_group_stocks"),
        t("output.search_group_futures"),
        t("output.search_group_warrants"),
        t("output.search_group_other"),
    ]

    for idx, group in enumerate(resp.results):
        title = t_term(group.title) if group.title else (group_titles[idx] if idx < len(group_titles) else t("output.search_group_n", n=idx+1))
        found_note = t("output.search_results_found", found=group.found)
        if group.found > len(group.hits):
            found_note = t("output.search_results_first", found=group.found, shown=len(group.hits))

        console.print(f"── [bold cyan]{title}[/bold cyan] {found_note} " + "─" * max(2, 40 - len(title) - len(found_note)))

        if not group.hits:
            console.print(f"  [dim]{t('output.search_no_results')}[/dim]\n")
            continue

        for hit in group.hits:
            doc = hit.document
            clean_title = escape(re.sub(r"</?mark>", "", doc.title))
            flags_str = " ".join([f"[bold yellow][{escape(f.upper())}][/bold yellow]" for f in doc.flags]) if doc.flags else ""
            console.print(f"  [bold green]{escape(doc.code):<8}[/bold green] {clean_title} {flags_str}")
        console.print()


def print_memos_table(memos: list[Memo], ticker_filter: str | None = None) -> None:
    """Prints user memos list in a table."""
    items = memos
    if ticker_filter:
        t_clean = ticker_filter.strip().upper()
        items = [m for m in items if m.code.upper() == t_clean]

    console.print(f"\n[bold]{t('output.memos_header', count=len(items))}[/bold]")

    table = Table(box=ROUNDED)
    table.add_column("ID", justify="right", style="dim")
    table.add_column(t("output.col_symbol"), style="bold cyan")
    table.add_column(t("output.col_content"), style="white")
    table.add_column(t("output.col_updated"), justify="right", style="dim")

    for m in items:
        date_str = m.updated_at.strftime("%d %b %Y %H:%M") if isinstance(m.updated_at, datetime) else str(m.updated_at)
        table.add_row(str(m.id), escape(m.code), escape(m.content), date_str)

    console.print(table)


def print_memo_action(action: str, memo_id: int, code: str = "", content: str = "") -> None:
    """Prints confirmation for memo create/update/delete."""
    if action == "add":
        console.print(f"[bold green]{t('output.memo_added', id=memo_id)}[/bold green]")
        console.print(f"[cyan]{escape(code)}[/cyan]: {escape(content)}")
    elif action == "update":
        console.print(f"[bold green]{t('output.memo_updated', id=memo_id)}[/bold green]")
        console.print(f"[cyan]{escape(code)}[/cyan]: {escape(content)}")
    elif action == "delete":
        console.print(f"[bold yellow]{t('output.memo_deleted', id=memo_id)}[/bold yellow]")


def print_fund_summary(fund: Fund, info: FundInfo) -> None:
    """Prints fund general info, yield analysis and portfolio."""
    # Fund Header
    mng_company = escape(fund.management_company.title) if fund.management_company else "—"
    price_str = f"{info.price:.6f} TL" if info.price is not None else "—"
    risk_str = f"{info.risk}/7" if info.risk is not None else "—"

    panel_text = (
        f"[bold cyan]{escape(fund.code)}[/bold cyan]  [bold white]{escape(fund.title)}[/bold white]\n"
        f"{t('output.fund_manager')} [dim]{mng_company}[/dim]  │  "
        f"{t('output.fund_price')} [yellow]{price_str}[/yellow]  │  "
        f"{t('output.fund_risk')} [red]{risk_str}[/red]"
    )
    if info.description:
        desc = (info.description[:250] + "...") if len(info.description) > 250 else info.description
        panel_text += f"\n\n[dim]{escape(desc)}[/dim]"

    console.print(Panel(panel_text, box=ROUNDED, border_style="cyan"))

    # Asset Allocation (Last Asset)
    if info.last_asset:
        table_asset = Table(title=f"── {t('output.fund_asset_allocation', date=info.last_asset_date or '')} ──", box=ROUNDED)
        table_asset.add_column(t("output.fund_asset_type"), style="cyan")
        table_asset.add_column(t("output.fund_ratio"), justify="right", style="green")

        for asset in info.last_asset:
            table_asset.add_row(t_term(asset.title), f"%{asset.value:.2f}")

        console.print(table_asset)

    # Portfolio
    if info.latest_portfolio and info.latest_portfolio.items:
        table_port = Table(title=f"── {t('output.fund_portfolio_breakdown', date=info.latest_portfolio.date)} ──", box=ROUNDED)
        table_port.add_column(t("output.col_stock"), style="bold yellow")
        table_port.add_column(t("output.fund_weight"), justify="right", style="green")
        table_port.add_column(t("output.fund_nominal"), justify="right")

        items_sorted = sorted(info.latest_portfolio.items, key=lambda x: x.weight, reverse=True)
        for item in items_sorted:
            table_port.add_row(item.code, f"%{item.weight:.2f}", abbreviate_number(item.nominal))

        console.print(table_port)

    # Yield Analysis
    if info.yield_:
        table_yield = Table(title=f"── {t('output.fund_yield_analysis')} ──", box=ROUNDED)
        table_yield.add_column(t("output.col_period"), style="cyan", no_wrap=True)
        table_yield.add_column(t("output.col_yield"), justify="right", style="bold green")

        labels = {
            "one_m": t("output.fund_1m"),
            "three_m": t("output.fund_3m"),
            "six_m": t("output.fund_6m"),
            "one_y": t("output.fund_1y"),
            "three_y": t("output.fund_3y"),
            "five_y": t("output.fund_5y"),
            "ytd": t("output.fund_ytd"),
        }

        for attr, label in labels.items():
            yd = getattr(info.yield_, attr)
            if yd and yd.yield_ is not None:
                color = "green" if yd.yield_ >= 0 else "red"
                table_yield.add_row(label, f"[{color}]%{yd.yield_:.2f}[/{color}]")

        console.print(table_yield)


def print_agenda_table(items: list[AgendaItem], time_label: str) -> None:
    """Prints agenda items grouped by day with type icons and detail data."""
    if not items:
        console.print(f"[dim]{t('output.agenda_empty', time_label=time_label)}[/dim]")
        return

    # Group by day (preserving order)
    from collections import defaultdict
    by_day: dict[str, list[AgendaItem]] = defaultdict(list)
    for item in items:
        by_day[str(item.day)].append(item)

    type_icons = {
        "dividend": "💰",
        "macro": "📊",
    }

    time_labels = {
        "today": t("output.agenda_today"),
        "thisWeek": t("output.agenda_this_week"),
        "nextWeek": t("output.agenda_next_week"),
    }
    header = time_labels.get(time_label, time_label)
    console.print(f"\n[bold]{t('output.agenda_header', header=header, count=len(items))}[/bold]")

    for day_str, day_items in by_day.items():
        # Day header
        try:
            from datetime import date as date_cls
            d = date_cls.fromisoformat(day_str)
            day_display = d.strftime("%d %B %Y, %A")
        except Exception:
            day_display = day_str

        console.print(f"\n  [bold cyan]── {day_display} ──[/bold cyan]")

        table = Table(box=ROUNDED, show_header=True, padding=(0, 1))
        table.add_column(t("output.col_type"), justify="center", no_wrap=True, width=4)
        table.add_column(t("output.col_time"), justify="center", no_wrap=True, style="dim", width=6)
        table.add_column(t("output.agenda_col_country"), justify="center", no_wrap=True, width=8)
        table.add_column(t("output.col_title"), style="white")
        table.add_column(t("output.agenda_col_detail"), style="dim")

        for item in day_items:
            icon = type_icons.get(item.type or "", "📋")
            time_str = item.time or "—"
            country = f"[bold]{item.image_fallback_text}[/bold]" if item.image_fallback_text else "[dim]—[/dim]"

            # Build detail string from data fields
            detail_parts = []
            for d in item.data:
                if d.label and d.value is not None:
                    detail_parts.append(f"{d.label}: [yellow]{d.value}[/yellow]")
            detail_str = "  ".join(detail_parts) if detail_parts else ""

            table.add_row(icon, time_str, country, item.title, detail_str)

        console.print(table)


# ─────────────────────────────────────────────────────────────────────────────
# Newsletter & Post – shared helpers
# ─────────────────────────────────────────────────────────────────────────────

_HTML_TAG_RE = re.compile(r"<[^>]+>")


def _strip_html(text: str) -> str:
    """Strips HTML tags and decodes common entities."""
    text = _HTML_TAG_RE.sub("", text)
    text = text.replace("&nbsp;", " ").replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    return text.strip()


def _render_editor_blocks(blocks: list) -> None:
    """Renders EditorJS blocks to the terminal (shared by newsletter & post)."""
    for block in blocks:
        btype = block.type.lower()
        data = block.data

        if btype == "paragraph":
            raw = data.get("text", "")
            text = re.sub(r"<b>(.*?)</b>", r"[bold]\1[/bold]", raw, flags=re.IGNORECASE)
            text = re.sub(r"<i>(.*?)</i>", r"[italic]\1[/italic]", text, flags=re.IGNORECASE)
            text = _strip_html(text)
            if text:
                console.print(f"  {text}")

        elif btype == "header":
            text = _strip_html(data.get("text", ""))
            level = data.get("level", 2)
            style = "bold cyan" if level <= 2 else "bold white"
            console.print(f"\n[{style}]{'─' * 4} {text} {'─' * 4}[/{style}]")

        elif btype == "image":
            url = data.get("file", {}).get("url", "")
            caption = _strip_html(data.get("caption", ""))
            parts = [f"[dim][🖼  {t('output.editor_image', url=url)}][/dim]"]
            if caption:
                parts.append(f"[dim italic]{caption}[/dim italic]")
            console.print("  " + "  ".join(parts))

        elif btype == "list":
            lst_style = data.get("style", "unordered")
            for idx, item in enumerate(data.get("items", []), 1):
                prefix = f"{idx}." if lst_style == "ordered" else "•"
                console.print(f"  {prefix} {_strip_html(str(item))}")

        elif btype == "quote":
            text = _strip_html(data.get("text", ""))
            caption = _strip_html(data.get("caption", ""))
            console.print(f"\n  [italic dim]❝ {text} ❞[/italic dim]")
            if caption:
                console.print(f"  [dim]— {caption}[/dim]")


# ─────────────────────────────────────────────────────────────────────────────
# Newsletter
# ─────────────────────────────────────────────────────────────────────────────

def print_newsletter_list(page, category_filter: str | None = None) -> None:
    """Prints newsletter list as a table."""
    items = page.results
    if category_filter:
        items = [i for i in items if (i.category and category_filter.lower() in i.category.title.lower())]

    total = len(items)
    more = page.count - total if page.count > total else 0
    more_str = t("output.more_suffix", count=more) if more else ""
    header = t("output.newsletters_header", total=total, more=more_str)
    console.print(f"\n[bold]{header}[/bold]")

    table = Table(box=ROUNDED)
    table.add_column(t("output.col_date"), justify="right", style="dim", no_wrap=True)
    table.add_column(t("output.col_category"), style="cyan", no_wrap=True)
    table.add_column(t("output.col_title"), style="white")
    table.add_column(t("output.col_author"), style="dim", no_wrap=True)
    table.add_column(t("output.col_slug"), style="dim")

    for item in items:
        date_str = item.published_at.strftime("%d %b %Y") if item.published_at else "—"
        cat_str = item.category.title if item.category else "—"
        author_str = item.author.name if item.author else "—"
        table.add_row(date_str, cat_str, escape(item.title), author_str, escape(item.slug))

    console.print(table)
    if page.next:
        console.print(f"[dim]{t('output.next_page_nav')}[/dim]")


def print_newsletter_detail(detail: NewsletterDetail) -> None:
    """Renders a newsletter's EditorJS content to the terminal."""
    date_str = detail.published_at.strftime("%d %B %Y, %H:%M") if detail.published_at else ""
    cat_str = detail.category.title if detail.category else ""
    author_str = detail.author.name if detail.author else ""
    subtitle = "  │  ".join(filter(None, [cat_str, author_str, date_str]))
    console.print(Panel(
        f"[bold white]{detail.title}[/bold white]\n[dim]{subtitle}[/dim]",
        box=ROUNDED, border_style="cyan",
    ))
    if not detail.content or not detail.content.blocks:
        console.print(f"[dim]{t('output.content_not_found')}[/dim]")
        return
    _render_editor_blocks(detail.content.blocks)
    console.print()


# ─────────────────────────────────────────────────────────────────────────────
# Posts
# ─────────────────────────────────────────────────────────────────────────────

def print_post_list(page, category_filter: str | None = None) -> None:
    """Prints post list as a table."""
    items = page.results
    if category_filter:
        items = [i for i in items if (i.category and category_filter.lower() in i.category.title.lower())]

    total = len(items)
    more = page.count - total if page.count > total else 0
    more_str = t("output.more_suffix", count=more) if more else ""
    header = t("output.posts_header", total=total, more=more_str)
    console.print(f"\n[bold]{header}[/bold]")

    table = Table(box=ROUNDED)
    table.add_column(t("output.col_date"), justify="right", style="dim", no_wrap=True)
    table.add_column(t("output.col_category"), style="cyan", no_wrap=True)
    table.add_column(t("output.col_title"), style="white")
    table.add_column(t("output.col_read_time"), justify="right", style="dim", no_wrap=True)
    table.add_column(t("output.col_pdf"), justify="center", no_wrap=True)
    table.add_column(t("output.col_slug"), style="dim")

    for item in items:
        date_str = item.created_at.strftime("%d %b %Y") if item.created_at else "—"
        cat_str = item.category.title if item.category else "—"
        read_str = t("output.min_abbr", count=item.read_time) if item.read_time else "—"
        pdf_str = "[green]✓[/green]" if item.pdf_attachment else "[dim]—[/dim]"
        table.add_row(date_str, cat_str, escape(item.title), read_str, pdf_str, escape(item.slug))

    console.print(table)
    if page.next:
        console.print(f"[dim]{t('output.next_page_nav')}[/dim]")


def print_post_detail(detail: PostDetail) -> None:
    """Renders a post's EditorJS content to the terminal."""
    date_str = detail.created_at.strftime("%d %B %Y") if detail.created_at else ""
    cat_str = detail.category.title if detail.category else ""
    author_str = detail.author.name if detail.author else ""
    read_str = t("output.min_read", count=detail.read_time) if detail.read_time else ""
    subtitle = "  │  ".join(filter(None, [cat_str, author_str, date_str, read_str]))

    panel_body = f"[bold white]{detail.title}[/bold white]\n[dim]{subtitle}[/dim]"
    if detail.description:
        panel_body += f"\n\n[dim italic]{detail.description}[/dim italic]"
    if detail.pdf_attachment:
        panel_body += f"\n\n[dim]📎 PDF: {detail.pdf_attachment}[/dim]"

    console.print(Panel(panel_body, box=ROUNDED, border_style="cyan"))

    if not detail.content or not detail.content.blocks:
        console.print(f"[dim]{t('output.content_not_found')}[/dim]")
    else:
        _render_editor_blocks(detail.content.blocks)

    # Benzer yazılar
    if detail.similars:
        console.print(f"\n[bold dim]── {t('output.similar_posts')} ──[/bold dim]")
        for s in detail.similars:
            cat = s.category.title if s.category else ""
            read = t("output.min_abbr", count=s.read_time) if s.read_time else ""
            console.print(f"  [cyan]{s.slug}[/cyan]  [dim]{cat}  {read}[/dim]  {s.title}")

    console.print()


# ─────────────────────────────────────────────────────────────────────────────
# Videos
# ─────────────────────────────────────────────────────────────────────────────

def print_video_list(page: VideoPage, filter_query: str | None = None, series_filter: str | None = None) -> None:
    """Prints video list as a table."""
    items = page.results
    if series_filter:
        items = [i for i in items if i.series and series_filter.lower() in (i.series.title or "").lower()]
    if filter_query:
        q = filter_query.lower()
        items = [i for i in items if q in i.title.lower() or (i.series and q in (i.series.title or "").lower())]

    total = len(items)
    more = page.count - total if page.count > total else 0
    more_str = t("output.more_suffix", count=more) if more else ""
    header = t("output.videos_header", total=total, more=more_str)
    console.print(f"\n[bold]{header}[/bold]")

    table = Table(box=ROUNDED)
    table.add_column(t("output.col_date"), justify="right", style="dim", no_wrap=True)
    table.add_column(t("output.col_series"), style="cyan", no_wrap=True)
    table.add_column(t("output.col_title"), style="white")
    table.add_column(t("output.col_duration"), justify="right", style="yellow", no_wrap=True)
    table.add_column(t("output.col_youtube"), style="red", no_wrap=True)
    table.add_column(t("output.col_slug"), style="dim")

    for item in items:
        date_str = item.published_at.strftime("%d %b %Y") if item.published_at else "—"
        series_str = item.series.title if item.series and item.series.title else "—"
        dur_str = item.duration if item.duration else "—"
        yt_str = item.youtube_url if item.youtube_url else "—"
        table.add_row(date_str, series_str, escape(item.title), dur_str, yt_str, escape(item.slug))

    console.print(table)
    if page.next:
        console.print(f"[dim]{t('output.next_page_nav')}[/dim]")


def print_video_detail(video: VideoItem) -> None:
    """Renders video details and description to the terminal."""
    date_str = video.published_at.strftime("%d %B %Y %H:%M") if video.published_at else ""
    series_str = video.series.title if video.series and video.series.title else ""
    dur_str = f"⏱️ {video.duration}" if video.duration else ""
    subtitle = "  │  ".join(filter(None, [series_str, date_str, dur_str]))

    panel_body = f"[bold white]{video.title}[/bold white]\n[dim]{subtitle}[/dim]"
    if video.youtube_url:
        panel_body += f"\n\n[bold red]▶ YouTube:[/bold red] [link={video.youtube_url}]{video.youtube_url}[/link]"

    console.print(Panel(panel_body, box=ROUNDED, border_style="red"))

    if video.series and video.series.description:
        console.print(f"[dim]{t('output.about_series', desc=video.series.description)}[/dim]\n")

    if video.description:
        console.print(f"[bold]{t('output.desc_and_chapters')}[/bold]")
        desc_lines = video.description.splitlines()
        for line in desc_lines:
            stripped = line.strip()
            if re.match(r"^\d{2}:\d{2}", stripped):
                console.print(f"  [cyan]{stripped}[/cyan]")
            elif stripped.startswith("▸") or stripped.startswith("👉") or stripped.startswith("📌") or stripped.startswith("#"):
                console.print(f"  [yellow]{stripped}[/yellow]")
            else:
                console.print(f"  {line}")
    console.print()


def print_notifications_table(page: NotificationPage) -> None:
    """Prints user notifications in a formatted table."""
    if not page.results:
        console.print(f"[dim]{t('output.notifications_empty')}[/dim]")
        return

    table = Table(
        title=f"🔔 {t('output.notifications_title')}",
        box=ROUNDED,
        header_style="bold cyan",
        show_lines=True,
    )
    table.add_column("ID", justify="right", style="dim", no_wrap=True)
    table.add_column(t("output.col_date"), style="cyan", no_wrap=True)
    table.add_column(t("output.col_message"), style="white")
    table.add_column(t("output.col_link"), style="blue")

    for item in page.results:
        date_str = item.created_at.strftime("%d %b %Y %H:%M") if isinstance(item.created_at, datetime) else str(item.created_at)
        link_str = item.web_url or item.app_url or "—"
        table.add_row(str(item.id), date_str, escape(item.message), link_str)

    console.print(table)
    if page.next:
        console.print(f"[dim]{t('output.notif_next_page')}[/dim]")


def print_notification_status(status: NotificationUnreadStatus) -> None:
    """Prints unread notifications status."""
    if status.has_unread:
        badge = f"[bold red]{t('output.notif_unread_badge')}[/bold red]"
    else:
        badge = f"[bold green]{t('output.notif_all_read_badge')}[/bold green]"

    if status.read_at:
        read_at_str = status.read_at.strftime("%d %b %Y %H:%M") if isinstance(status.read_at, datetime) else str(status.read_at)
        time_text = f"[dim]{t('output.notif_last_read_time', time=read_at_str)}[/dim]"
    else:
        time_text = f"[dim]{t('output.notif_last_read_none')}[/dim]"

    panel = Panel(
        f"{badge}\n{time_text}",
        title=f"🔔 {t('output.notif_status_title')}",
        box=ROUNDED,
        border_style="yellow" if status.has_unread else "green",
    )
    console.print(panel)


def print_notification_action(action: str = "mark_read", status: str = "success") -> None:
    """Prints confirmation for notification actions."""
    if action == "mark_read":
        if status == "success":
            console.print(f"[bold green]{t('output.notif_mark_read_success')}[/bold green]")
        else:
            console.print(f"[bold yellow]{t('output.notif_action_status', status=status)}[/bold yellow]")


