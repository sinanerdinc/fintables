"""Centralized internationalization (i18n) module for Fintables.

Contains all localized strings for CLI descriptions, parameters, options,
errors, and Rich terminal output formatters.
"""

import locale
import os
import sys

_current_language: str | None = None

# ─────────────────────────────────────────────────────────────────────────────
# Translations Dictionary (Add new languages like 'de', 'es' here)
# ─────────────────────────────────────────────────────────────────────────────

TRANSLATIONS: dict[str, dict[str, str]] = {
    "en": {
        # Common / Errors
        "error.prefix": "[bold red]Error:[/bold red]",
        "error.unknown_subcommand": "Unknown subcommand: '{subcommand}'. Supported: {supported}",
        "error.auth_required": "Authentication is required for this operation. Please set FINTABLES_USERNAME or FINTABLES_EMAIL and FINTABLES_PASSWORD in your .env file.",
        "error.session_expired": "Session expired or authentication failed.",
        "error.not_found": "Requested resource not found (404): {url}",
        "error.api_error": "API error ({status}): {detail}",
        "error.login_request_failed": "An error occurred during login request: {error}",
        "error.login_failed": "Login failed: {detail}. Please check your FINTABLES_USERNAME/FINTABLES_EMAIL and FINTABLES_PASSWORD settings.",
        "error.refresh_failed": "An error occurred during token refresh: {error}",
        "error.refresh_unsuccessful": "Token refresh failed. Please log in again.",
        "common.yes": "Yes",
        "common.no": "No",

        # CLI App & Callbacks
        "cli.app.help": "Fintables Mobile API Client and CLI Tool",
        "cli.app.version_help": "Shows Fintables version",
        "cli.app.lang_help": "Language selection (en, tr)",

        # CLI Top-level Command Descriptions
        "cli.cmd.company": "Fetches company profile and ratio types",
        "cli.cmd.symbol": "Fetches stock summary or financial statements (sheets)",
        "cli.cmd.analyst": "Fetches analyst forecasts and price targets",
        "cli.cmd.search": "Searches stocks, futures, and warrants",
        "cli.cmd.feed": "Fetches news feed and public disclosure (KAP) items",
        "cli.cmd.fund": "Fetches mutual fund details and portfolio breakdown",
        "cli.cmd.agenda": "Fetches economic calendar and dividend agenda",
        "cli.cmd.watchlist": "Manages favorite stock watchlist",
        "cli.cmd.memo": "Manages memos attached to stocks (add, list, update, delete)",
        "cli.cmd.auth": "Authentication operations",
        "cli.cmd.portfolio": "Virtual portfolio management",
        "cli.cmd.newsletter": "Fintables newsletters",
        "cli.cmd.post": "Fintables research articles and company notes",
        "cli.cmd.video": "Fintables YouTube and stock market videos",
        "cli.cmd.notification": "Displays and manages Fintables notifications",
        "cli.cmd.shell": "Starts interactive REPL shell session",

        # CLI Shared Options & Arguments
        "cli.common.output_help": "Output format: table or json",
        "cli.common.ticker_help": "Stock symbol (e.g. ASELS, FROTO)",

        # CLI: Symbol
        "cli.symbol.subcommand_help": "Subcommand: summary or sheets",
        "cli.symbol.sheet_help": "Financial statement to display: balance, income, cashflow, or all",
        "cli.symbol.periods_help": "Number of periods to display",
        "cli.symbol.quarterly_help": "Show quarterly data instead of cumulative",

        # CLI: Analyst
        "cli.analyst.brokerage_help": "Filter by specific brokerage (e.g. PHC, IYM)",
        "cli.analyst.model_portfolio_help": "Show only brokerages in model portfolio",

        # CLI: Search
        "cli.search.query_help": "Query to search (e.g. ASELS, SASA, Polyester)",

        # CLI: Feed
        "cli.feed.ticker_help": "Stock symbol (e.g. FROTO). If not specified, fetches global feed.",
        "cli.feed.type_help": "Content type filter: post, news, newsletter, article",
        "cli.feed.importance_help": "Importance filter: low, mid, high",
        "cli.feed.page_size_help": "Items per page",
        "cli.feed.cursor_help": "Pagination cursor (for subsequent pages)",

        # CLI: Fund
        "cli.fund.ticker_help": "Fund code (e.g. TLY, MAC)",

        # CLI: Agenda
        "cli.agenda.time_help": "Time range: today | thisWeek | nextWeek",
        "cli.agenda.type_help": "Type filter: dividend | macro",
        "cli.agenda.invalid_time": "Invalid time range: '{time}'. Options: {options}",

        # CLI: Watchlist
        "cli.watchlist.add_help": "Adds a stock to favorites.",
        "cli.watchlist.remove_help": "Removes a stock from favorites.",

        # CLI: Memo
        "cli.memo.list_help": "Lists all saved memos.",
        "cli.memo.add_help": "Adds a new memo to a stock.",
        "cli.memo.update_help": "Updates an existing memo.",
        "cli.memo.delete_help": "Deletes a memo.",
        "cli.memo.code_help": "Stock code (e.g. FROTO)",
        "cli.memo.content_help": "Note content",
        "cli.memo.id_help": "Memo ID",

        # CLI: Auth
        "cli.auth.login_help": "Logs in with email and password to test connection.",
        "cli.auth.email_help": "Fintables email address",
        "cli.auth.username_help": "Fintables username / email",
        "cli.auth.password_help": "Fintables password",
        "cli.auth.missing_credentials": "Email or password not provided. Please provide them as arguments or define FINTABLES_EMAIL / FINTABLES_USERNAME and FINTABLES_PASSWORD in your .env file.",
        "cli.auth.login_success": "✅ Login successful!",
        "cli.auth.access_token": "Access Token: [dim]{token}...[/dim]",

        # CLI: Portfolio
        "cli.portfolio.list_help": "Lists virtual portfolios.",
        "cli.portfolio.create_help": "Creates a new virtual portfolio.",
        "cli.portfolio.delete_help": "Deletes a virtual portfolio.",
        "cli.portfolio.rename_help": "Renames a portfolio.",
        "cli.portfolio.show_help": "Shows positions in a portfolio.",
        "cli.portfolio.buy_help": "Adds a buy transaction to a portfolio.",
        "cli.portfolio.sell_help": "Adds a sell transaction to a portfolio.",
        "cli.portfolio.name_or_uuid_help": "Portfolio name or UUID",
        "cli.portfolio.create_title_help": "Portfolio name",
        "cli.portfolio.rename_title_help": "New portfolio name",
        "cli.portfolio.ticker_help": "Stock symbol (e.g. SASA)",
        "cli.portfolio.amount_help": "Quantity",
        "cli.portfolio.price_help": "Buy price",
        "cli.portfolio.sell_price_help": "Sell price",
        "cli.portfolio.date_help": "Transaction date (YYYY-MM-DD)",
        "cli.portfolio.not_found": "Portfolio not found: '{identifier}'",
        "cli.portfolio.multiple_found": "Multiple portfolios found with name '{identifier}'. Please use UUID instead.",
        "cli.portfolio.empty": "No portfolios yet.",
        "cli.portfolio.created": "✅ Portfolio created: [bold cyan]{title}[/bold cyan] [dim]({id})[/dim]",
        "cli.portfolio.deleted": "✅ Portfolio deleted: [bold cyan]{identifier}[/bold cyan]",
        "cli.portfolio.renamed": "✅ Portfolio renamed: [bold cyan]{old_title}[/bold cyan] → [bold green]{new_title}[/bold green]",
        "cli.portfolio.buy_success": "✅ Buy transaction added: {portfolio} | {ticker} | {amount} @ {price}",
        "cli.portfolio.sell_success": "✅ Sell transaction added: {portfolio} | {ticker} | {amount} @ {price}",
        "cli.portfolio.positions_empty": "No positions found in portfolio. ({title})",
        "cli.portfolio.table_title": "Portfolios",
        "cli.portfolio.col_id": "ID / UUID",
        "cli.portfolio.col_title": "Portfolio Name",
        "cli.portfolio.pos_title": "Portfolio: {title}",
        "cli.portfolio.col_stock": "Stock",
        "cli.portfolio.col_quantity": "Quantity",
        "cli.portfolio.col_avg_cost": "Avg Cost",
        "cli.portfolio.col_current_price": "Current Price",
        "cli.portfolio.col_total_value": "Total Value",
        "cli.portfolio.col_return_pct": "Return %",
        "cli.portfolio.col_total_cost": "Total Cost",
        "cli.portfolio.col_gain_loss": "Gain/Loss",
        "cli.portfolio.col_gain_loss_pct": "Gain/Loss %",
        "cli.portfolio.available_portfolios": "Available portfolios: {names}",
        "cli.portfolio.use_uuid": "Please use UUID directly: {ids}",
        "cli.portfolio.total_row": "TOTAL",

        # CLI: Newsletter
        "cli.newsletter.list_help": "Lists newsletters.",
        "cli.newsletter.read_help": "Reads newsletter content.",
        "cli.newsletter.category_help": "Category filter",
        "cli.newsletter.page_help": "Page number",
        "cli.newsletter.slug_help": "Newsletter slug (e.g. bulten-123)",

        # CLI: Post
        "cli.post.list_help": "Lists research articles and company notes.",
        "cli.post.read_help": "Reads article content (content + similar articles).",
        "cli.post.category_help": "Category filter",
        "cli.post.page_help": "Page number",
        "cli.post.slug_help": "Post slug (e.g. sasa-analiz)",

        # CLI: Video
        "cli.video.list_help": "Lists videos.",
        "cli.video.show_help": "Shows video details, description, and YouTube link.",
        "cli.video.type_help": "Content type (e.g. video)",
        "cli.video.filter_help": "Search in title/series",
        "cli.video.series_help": "Series filter",
        "cli.video.page_help": "Page number",
        "cli.video.slug_help": "Video slug",

        # CLI: Notification
        "cli.notification.list_help": "Lists notifications.",
        "cli.notification.unread_help": "Displays unread notification status and last read timestamp.",
        "cli.notification.status_help": "Displays unread notification status and last read timestamp (alias for unread).",
        "cli.notification.mark_read_help": "Marks all notifications as read.",
        "cli.notification.page_size_help": "Number of notifications to fetch (default: 100)",

        # Formatter / Output: Company & Symbol
        "output.inflation_accounting": "Inflation Accounting",
        "output.participation_index": "Participation Index",
        "output.col_category": "Category",
        "output.col_ratio": "Ratio",
        "output.col_access": "Access",
        "output.ratio_types": "Ratio Types:",
        "output.col_code": "Code",
        "output.col_title": "Title",
        "output.col_group": "Group",
        "output.col_item": "Item",
        "output.col_value": "Value",
        "output.col_period": "Period",
        "output.col_yield": "Yield",
        "output.col_initial": "Initial",
        "output.col_low": "Low",
        "output.col_high": "High",
        "output.period_1w": "1 Week",
        "output.col_brokerage": "Brokerage",
        "output.col_portfolio": "Portfolio",
        "output.col_importance": "Importance",
        "output.col_company": "Company",
        "output.feed_general": "General ",
        "output.feed_importance_high": "[bold red]●●● HIGH[/bold red]",
        "output.feed_importance_mid": "[bold yellow]●○○ MID [/bold yellow]",
        "output.feed_importance_low": "[dim green]○○○ LOW [/dim green]",
        "output.watchlist_empty": "(empty)",
        "output.search_group_stocks": "Stocks",
        "output.search_group_futures": "Futures",
        "output.search_group_warrants": "Warrants",
        "output.search_group_other": "Other",
        "output.search_group_n": "Group {n}",
        "output.search_results_found": "({found} results)",
        "output.search_results_first": "({found} results, showing first {shown})",
        "output.col_symbol": "Symbol",
        "output.col_content": "Content",
        "output.col_updated": "Updated",
        "output.col_stock": "Stock",
        "output.col_weight": "Weight",
        "output.col_nominal": "Nominal",
        "output.sheet_cash_flow": "Cash Flow",

        # Formatter / Output: Analyst Ratings
        "output.analyst_ratings_header": "{ticker} — Analyst Ratings ({count} institutions)",
        "output.col_institution": "Institution",
        "output.col_target_price": "Target Price",
        "output.col_upside": "Upside",
        "output.col_rating": "Rating",
        "output.min_target": "Min Target:",
        "output.avg_target": "Avg Target:",
        "output.max_target": "Max Target:",
        "output.badge_buy": "BUY",
        "output.badge_hold": "HOLD",
        "output.badge_sell": "SELL",
        "output.badge_outperform": "OUTPERFORM",
        "output.badge_market_perform": "MARKET PERFORM",
        "output.badge_underperform": "UNDERPERFORM",

        # Formatter / Output: Sheets
        "output.sheet_balance": "Balance Sheet",
        "output.sheet_income": "Income Statement",
        "output.sheet_cashflow": "Cash Flow Statement",
        "output.sheet_quarterly": "Quarterly",
        "output.sheet_cumulative": "Cumulative",
        "output.inflation_note": "ℹ️  Data is inflation-adjusted and consolidated.",

        # Formatter / Output: Feed
        "output.feed_header": "{ticker}News Feed ({count} items)",
        "output.col_date": "Date",
        "output.col_time": "Time",
        "output.col_type": "Type",
        "output.col_related": "Related",
        "output.next_page_note": "ℹ️  Next page available. (Increase with --page-size)",

        # Formatter / Output: Watchlist
        "output.watchlist_added": "✅  {ticker} added to watchlist.",
        "output.watchlist_removed": "🗑️  {ticker} removed from watchlist.",
        "output.watchlist_label": "Watchlist: {items}",

        # Formatter / Output: Search
        "output.search_header": 'Search: "{query}"',
        "output.search_no_results": "(No results)",

        # Formatter / Output: Memos
        "output.memos_header": "Your Memos ({count} items)",
        "output.col_stock": "Stock",
        "output.col_note": "Note",
        "output.memo_added": "✅  Memo added (ID: {id})",
        "output.memo_updated": "✅  Memo updated (ID: {id})",
        "output.memo_deleted": "🗑️  Memo deleted (ID: {id})",

        # Formatter / Output: Funds
        "output.fund_manager": "Manager:",
        "output.fund_price": "Price:",
        "output.fund_risk": "Risk:",
        "output.fund_asset_allocation": "Asset Allocation ({date})",
        "output.fund_asset_type": "Asset Type",
        "output.fund_ratio": "Ratio",
        "output.fund_portfolio_breakdown": "Portfolio Breakdown ({date})",
        "output.fund_weight": "Weight",
        "output.fund_nominal": "Nominal",
        "output.fund_yield_analysis": "Yield Analysis",
        "output.fund_1m": "1 Month",
        "output.fund_3m": "3 Months",
        "output.fund_6m": "6 Months",
        "output.fund_1y": "1 Year",
        "output.fund_3y": "3 Years",
        "output.fund_5y": "5 Years",
        "output.fund_ytd": "Year to Date (YTD)",

        # Formatter / Output: Agenda
        "output.agenda_empty": "No agenda found for this period ({time_label}).",
        "output.agenda_today": "Today",
        "output.agenda_this_week": "This Week",
        "output.agenda_next_week": "Next Week",
        "output.agenda_header": "Agenda — {header} ({count} events)",
        "output.agenda_col_country": "Country/Source",
        "output.agenda_col_detail": "Detail",

        # Formatter / Output: Editor Blocks & Content
        "output.editor_image": "Image: {url}",
        "output.newsletters_header": "Newsletters ({total} results{more})",
        "output.more_suffix": ", +{count} more",
        "output.col_category": "Category",
        "output.col_author": "Author",
        "output.col_slug": "Slug",
        "output.next_page_nav": "ℹ️  Next page available (use --page to navigate)",
        "output.content_not_found": "(Content not found)",

        # Formatter / Output: Posts
        "output.posts_header": "Posts ({total} results{more})",
        "output.col_read_time": "Read Time",
        "output.col_pdf": "PDF",
        "output.min_abbr": "{count} min",
        "output.min_read": "{count} min read",
        "output.similar_posts": "Similar Posts",

        # Formatter / Output: Videos
        "output.videos_header": "Videos ({total} results{more})",
        "output.col_series": "Series",
        "output.col_duration": "Duration",
        "output.col_youtube": "YouTube",
        "output.about_series": "About Series: {desc}",
        "output.desc_and_chapters": "Description & Chapters",

        # Formatter / Output: Notifications
        "output.notifications_title": "Notifications",
        "output.notifications_empty": "No notifications found.",
        "output.col_message": "Message",
        "output.col_link": "Link",
        "output.notif_next_page": "ℹ️  Next page available (increase with --page-size)",
        "output.notif_unread_badge": "🔴 You have unread notifications.",
        "output.notif_all_read_badge": "🟢 All notifications have been read.",
        "output.notif_last_read_time": "Last read time: {time}",
        "output.notif_last_read_none": "Last read time: —",
        "output.notif_status_title": "Notification Status",
        "output.notif_mark_read_success": "✅ All notifications marked as read.",
        "output.notif_action_status": "⚠️  Action status: {status}",
        "output.eligible": "Eligible",
        "output.not_eligible": "Not Eligible",

        # Financial Terms & Section Titles (API translations)
        "term.Çarpanlar": "Multipliers",
        "term.Şirket Detayları": "Company Details",
        "term.Şirketler": "Companies",
        "term.Özet Gelir Tablosu": "Income Statement Summary",
        "term.Özet Bilanço": "Balance Sheet Summary",
        "term.Getiri Analizi": "Yield Analysis",
        "term.Fiili Dolaşım Oranı": "Free Float Ratio",
        "term.Piyasa Değeri": "Market Cap",
        "term.Hisse Başına Kar": "Earnings Per Share (EPS)",
        "term.Ödenmiş Sermaye": "Paid-in Capital",
        "term.Katılım Endeksi": "Participation Index",
        "term.F/K": "P/E",
        "term.FD/FAVÖK": "EV/EBITDA",
        "term.PD/DD": "P/B",
        "term.Net Borç/FAVÖK": "Net Debt/EBITDA",
        "term.Satışlar": "Sales / Revenue",
        "term.Brüt Kar": "Gross Profit",
        "term.Esas Faaliyet Karı": "Operating Profit",
        "term.FAVÖK": "EBITDA",
        "term.Net Dönem Karı": "Net Income",
        "term.Dönen Varlıklar": "Current Assets",
        "term.Duran Varlıklar": "Non-Current Assets",
        "term.Toplam Varlıklar": "Total Assets",
        "term.Kısa Vadeli Yükümlülükler": "Current Liabilities",
        "term.Uzun Vadeli Yükümlülükler": "Non-Current Liabilities",
        "term.Toplam Yükümlülükler": "Total Liabilities",
        "term.Toplam Kaynaklar": "Total Liabilities and Equity",
        "term.Finansal Borçlar": "Financial Debt",
        "term.Net Borç": "Net Debt",
        "term.Özkaynaklar": "Total Equity",
        "term.Nakit ve Nakit Benzerleri": "Cash and Cash Equivalents",
        "term.Ticari Alacaklar": "Trade Receivables",
        "term.Ticari Borçlar": "Trade Payables",
        "term.Stoklar": "Inventories",
        "term.Maddi Duran Varlıklar": "Property, Plant and Equipment",
        "term.Maddi Olmayan Duran Varlıklar": "Intangible Assets",
        "term.Yatırım Amaçlı Gayrimenkuller": "Investment Properties",
        "term.Ertelenmiş Vergi Varlığı": "Deferred Tax Asset",
        "term.Ertelenmiş Vergi Yükümlülüğü": "Deferred Tax Liability",
        "term.Satışların Maliyeti": "Cost of Sales",
        "term.Satış Gelirleri": "Sales Revenue",
        "term.Brüt Kar (Zarar)": "Gross Profit (Loss)",
        "term.Esas Faaliyet Karı (Zararı)": "Operating Profit (Loss)",
        "term.Finansman Gelirleri": "Financial Income",
        "term.Finansman Giderleri": "Financial Expenses",
        "term.Ertelenmiş Vergi Geliri": "Deferred Tax Income",
        "term.Ertelenmiş Vergi Gideri": "Deferred Tax Expense",
        "term.Ertelenmiş Vergi Geliri (Gideri)": "Deferred Tax Income (Expense)",
        "term.Vergi Öncesi Kar": "Profit Before Tax",
        "term.Dönem Karı": "Net Income for the Period",
        "term.Net Dönem Karı (Zararı)": "Net Income (Loss) for the Period",
        "term.İşletme Faaliyetlerinden Nakit Akışları": "Cash Flows from Operating Activities",
        "term.İşletme Faaliyetlerinden Kaynaklanan Nakit Akışları": "Cash Flows from Operating Activities",
        "term.Yatırım Faaliyetlerinden Nakit Akışları": "Cash Flows from Investing Activities",
        "term.Yatırım Faaliyetlerinden Kaynaklanan Nakit Akışları": "Cash Flows from Investing Activities",
        "term.Finansman Faaliyetlerinden Nakit Akışları": "Cash Flows from Financing Activities",
        "term.Finansman Faaliyetlerinden Kaynaklanan Nakit Akışları": "Cash Flows from Financing Activities",
        "term.Kısa Vadeli Borçlanmalar": "Short Term Borrowings",
        "term.Uzun Vadeli Borçlanmalar": "Long Term Borrowings",
        "term.Diğer Alacaklar": "Other Receivables",
        "term.Diğer Borçlar": "Other Payables",
        "term.Finansal Yatırımlar": "Financial Investments",
        
        # Comprehensive Balance Sheet Additions
        "term.Türev Araçlar": "Derivative Financial Instruments",
        "term.Peşin Ödenmiş Giderler": "Prepaid Expenses",
        "term.Cari Dönem Vergisiyle İlgili Varlıklar": "Current Income Tax Assets",
        "term.Diğer Dönen Varlıklar": "Other Current Assets",
        "term.Satış Amacıyla Elde Tutulan Duran Varlıklar": "Non-Current Assets Held for Sale",
        "term.Diğer Duran Varlıklar": "Other Non-Current Assets",
        "term.Çalışanlara Sağlanan Faydalar Kapsamında Borçlar": "Payables for Employee Benefits",
        "term.Müşteri Sözleşmelerinden Doğan Varlıklar": "Assets from Customer Contracts",
        "term.Müşteri Sözleşmelerinden Doğan Yükümlülükler": "Liabilities from Customer Contracts",
        "term.Ertelenmiş Gelirler": "Deferred Income",
        "term.Dönem Karı Vergi Yükümlülüğü": "Current Income Tax Liability",
        "term.Kısa Vadeli Karşılıklar": "Current Provisions",
        "term.Diğer Kısa Vadeli Yükümlülükler": "Other Current Liabilities",
        "term.Uzun vadeli Karşılıklar": "Non-Current Provisions",
        "term.Diğer Uzun Vadeli Yükümlülükler": "Other Non-Current Liabilities",
        "term.Ana Ortaklığa Ait Özkaynaklar": "Equity Attributable to Owners of Parent",
        "term.Sermaye Düzeltme Farkları": "Inflation Adjustments to Share Capital",
        "term.Geri Alınmış Paylar (-)": "Treasury Shares (-)",
        "term.Paylara İlişkin Primler (İskontolar)": "Share Premiums (Discounts)",
        "term.Kar veya Zararda Yeniden Sınıflandırılmayacak Birikmiş Diğer Kapsamlı Gelirler (Giderler)": "Other Comprehensive Income (Loss) Not Reclassified to Profit or Loss",
        "term.Kar veya Zararda Yeniden Sınıflandırılmayacak Birikmiş Diğer Kapsamlı Gelirler": "Other Comprehensive Income Not Reclassified to Profit or Loss",
        "term.Kar veya Zararda Yeniden Sınıflandırılacak Birikmiş Diğer Kapsamlı Gelirler (Giderler)": "Other Comprehensive Income (Loss) Reclassified to Profit or Loss",
        "term.Kar veya Zararda Yeniden Sınıflandırılacak Birikmiş Diğer Kapsamlı Gelirler": "Other Comprehensive Income Reclassified to Profit or Loss",
        "term.(Giderler)": "(Expenses)",
        "term.Kardan Ayrılan Kısıtlanmış Yedekler": "Restricted Reserves Appropriated from Profit",
        "term.Diğer Yedekler": "Other Reserves",
        "term.Geçmiş Yıllar Kar/Zararları": "Prior Years' Profits (Losses)",
        "term.Dönem Net Kar/Zararı": "Net Profit (Loss) for the Period",
        "term.Hedge Dahil Net Yabancı Para Pozisyonu": "Net Foreign Currency Position Including Hedging",
        "term.İştirakler, İş Ortaklıkları ve Bağlı Ortaklıklardaki Yatırımlar": "Investments in Associates, Joint Ventures and Subsidiaries",
        "term.Özkaynak Yöntemiyle Değerlenen Yatırımlar": "Investments Accounted for Using Equity Method",
        "term.Kullanım Hakkı Varlıkları": "Right-of-Use Assets",
        
        # Comprehensive Income Statement Additions
        "term.Yurt İçi Satışlar": "Domestic Sales",
        "term.Yurt Dışı Satışlar": "Foreign Sales",
        "term.Satışların Maliyeti (-)": "Cost of Sales (-)",
        "term.Ticari Faaliyetlerden Brüt Kar (Zarar)": "Gross Profit (Loss) from Commercial Operations",
        "term.Genel Yönetim Giderleri (-)": "General Administrative Expenses (-)",
        "term.Pazarlama, Satış ve Dağıtım Giderleri (-)": "Marketing, Selling and Distribution Expenses (-)",
        "term.Araştırma ve Geliştirme Giderleri (-)": "Research and Development Expenses (-)",
        "term.Diğer Faaliyet Gelirleri": "Other Operating Income",
        "term.Diğer Faaliyet Giderleri (-)": "Other Operating Expenses (-)",
        "term.Faaliyet Karı (Zararı)": "Operating Profit (Loss)",
        "term.Yatırım Faaliyetlerinden Gelirler": "Income from Investing Activities",
        "term.Yatırım Faaliyetlerinden Giderler (-)": "Expenses from Investing Activities (-)",
        "term.Özkaynak Yöntemiyle Değerlenen Yatırımların Karlarından (Zararlarından) Paylar": "Share of Profit (Loss) of Investments Accounted for Using Equity Method",
        "term.Finansman Geliri (Gideri) Öncesi Faaliyet Karı (Zararı)": "Operating Profit (Loss) Before Financial Income (Expense)",
        "term.(Esas Faaliyet Dışı) Finansal Gelirler": "Financial Income (Non-Operating)",
        "term.(Esas Faaliyet Dışı) Finansal Giderler (-)": "Financial Expenses (Non-Operating) (-)",
        "term.Net Parasal Pozisyon Kazançları (Kayıpları)": "Net Monetary Position Gains (Losses)",
        "term.Sürdürülen Faaliyetler Vergi Öncesi Karı (Zararı)": "Profit (Loss) Before Tax from Continuing Operations",
        "term.Sürdürülen Faaliyetler Vergi Geliri (Gideri)": "Tax Income (Expense) from Continuing Operations",
        "term.Dönem Vergi Geliri (Gideri)": "Tax Income (Expense) for the Period",
        "term.Sürdürülen Faaliyetler Dönem Karı/Zararı": "Profit (Loss) from Continuing Operations",
        "term.Dönem Karı (Zararı)": "Profit (Loss) for the Period",
        "term.Azınlık Payları": "Non-Controlling Interests",
        "term.Ana Ortaklık Payları": "Attributable to Owners of Parent",
        "term.Amortisman": "Depreciation and Amortization",
        
        # Comprehensive Cash Flow Statement Additions
        "term.Dönem Net Karı (Zararı) Mutabakatı İle İlgili Düzeltmeler": "Adjustments to Reconcile Net Profit (Loss)",
        "term.Amortisman ve İtfa Gideri İle İlgili Düzeltmeler": "Adjustments for Depreciation and Amortization",
        "term.Değer Düşüklüğü (İptali) İle İlgili Düzeltmeler": "Adjustments for Impairment Loss (Reversal)",
        "term.Karşılıklar İle İlgili Düzeltmeler": "Adjustments for Provisions",
        "term.Faiz (Gelirleri) ve Giderleri İle İlgili Düzeltmeler": "Adjustments for Interest (Income) and Expenses",
        "term.Kar Payı (Geliri) Gideri ile İlgili Düzeltmeler": "Adjustments for Dividend (Income) Expense",
        "term.Vergi (Geliri) Gideri İle İlgili Düzeltmeler": "Adjustments for Tax (Income) Expense",
        "term.Gerçekleşmemiş Yabancı Para Çevrim Farkları İle İlgili Düzeltmeler": "Adjustments for Unrealized Foreign Exchange Differences",
        "term.Gerçeğe Uygun Değer Kayıpları (Kazançları) İle İlgili Düzeltmeler": "Adjustments for Fair Value Losses (Gains)",
        "term.Özkaynak Yöntemiyle Değerlenen Yatırımların Dağıtılmamış Karları ile İlgili Düzeltmeler": "Adjustments for Undistributed Profits of Associates",
        "term.Duran Varlıkların Elden Çıkarılmasından Kaynaklanan Kayıplar (Kazançlar) İle İlgili Düzeltmeler": "Adjustments for Losses (Gains) on Disposal of Non-Current Assets",
        "term.Satış Amaçlı veya Ortaklara Dağıtılmak Üzere Elde Tutulan Duran Varlıkların Elden Çıkarılmasından Kaynaklanan Kayıplar (Kazançlar) ile İlgili Düzeltmeler": "Adjustments for Losses (Gains) on Disposal of Assets Held for Sale",
        "term.Kar (Zarar) Mutabakatı İle İlgili Diğer Düzeltmeler": "Other Adjustments to Reconcile Profit (Loss)",
        "term.Yatırım ya da Finansman Faaliyetlerinden Kaynaklanan Nakit Akışlarına Neden Olan Diğer Kalemlere İlişkin Düzeltmeler": "Adjustments for Other Items Related to Investing or Financing Cash Flows",
        "term.İşletme Sermayesinde Gerçekleşen Değişimler": "Changes in Working Capital",
        "term.Ticari Alacaklardaki Azalış (Artış) ile İlgili Düzeltmeler": "Adjustments for Decrease (Increase) in Trade Receivables",
        "term.Faaliyetlerle İlgili Diğer Alacaklardaki Azalış (Artış) ile İlgili Düzeltmeler": "Adjustments for Decrease (Increase) in Other Receivables from Operations",
        "term.Stoklardaki Azalışlar (Artışlar) İle İlgili Düzeltmeler": "Adjustments for Decrease (Increase) in Inventories",
        "term.Peşin Ödenmiş Giderlerdeki Azalış (Artış)": "Decrease (Increase) in Prepaid Expenses",
        "term.Ticari Borçlardaki Artış (Azalış) ile İlgili Düzeltmeler": "Adjustments for Increase (Decrease) in Trade Payables",
        "term.Çalışanlara Sağlanan Faydalar Kapsamında Borçlardaki Artış (Azalış)": "Increase (Decrease) in Payables for Employee Benefits",
        "term.Müşteri Sözleşmelerinden Doğan Yükümlülüklerdeki Artış (Azalış) İle İlgili Düzeltmeler": "Adjustments for Increase (Decrease) in Liabilities from Customer Contracts",
        "term.Faaliyetler ile İlgili Diğer Borçlardaki Artış (Azalış) ile İlgili Düzeltmeler": "Adjustments for Increase (Decrease) in Other Payables from Operations",
        "term.Ertelenmiş Gelirlerdeki Artış (Azalış)": "Increase (Decrease) in Deferred Income",
        "term.İşletme Sermayesinde Gerçekleşen Diğer Artış (Azalış) ile İlgili Düzeltmeler": "Adjustments for Other Increase (Decrease) in Working Capital",
        "term.Faaliyetlerden Elde Edilen Nakit Akışları": "Cash Flows Generated from Operations",
        "term.Ödenen Temettüler": "Dividends Paid",
        "term.Alınan Temettüler": "Dividends Received",
        "term.Vergi İadeleri (Ödemeleri)": "Tax Returns (Payments)",
        "term.Çalışanlara Sağlanan Faydalara İlişkin Karşılıklar Kapsamında Yapılan Ödemeler": "Payments Related to Provisions for Employee Benefits",
        "term.Diğer Karşılıklara İlişkin Ödemeler": "Payments Related to Other Provisions",
        "term.Diğer Nakit Girişleri (Çıkışları)": "Other Cash Inflows (Outflows)",
        "term.Maddi ve Maddi Olmayan Duran Varlıkların Satışından Kaynaklanan Nakit Girişleri": "Cash Inflows from Sale of Property, Plant and Equipment and Intangible Assets",
        "term.Maddi ve Maddi Olmayan Duran Varlıkların Alımından Kaynaklanan Nakit Çıkışları": "Cash Outflows from Purchase of Property, Plant and Equipment and Intangible Assets",
        "term.Yatırım Amaçlı Gayrimenkul Satımından Kaynaklanan Nakit Girişleri": "Cash Inflows from Sale of Investment Properties",
        "term.Satış Amacıyla Elde Tutulan Duran Varlık Satışlarından Kaynaklanan Nakit Girişleri": "Cash Inflows from Sale of Assets Held for Sale",
        "term.Bağlı Ortaklıkların Kontrolünün Elde Edilmesine Yönelik Alışlara İlişkin Nakit Çıkışları": "Cash Outflows from Acquisition of Control of Subsidiaries",
        "term.İştiraklar ve/veya İş Ortaklıkları Pay Alımı veya Sermaye Artırımı Sebebiyle Oluşan Nakit Çıkışları": "Cash Outflows from Purchase of Shares or Capital Increase of Associates and/or Joint Ventures",
        "term.Verilen Nakit Avans ve Borçlar": "Cash Advances and Loans Granted",
        "term.Verilen Nakit Avans ve Borçlardan Geri Ödemeler": "Repayments of Cash Advances and Loans Granted",
        "term.Alınan Faiz": "Interest Received",
        "term.Pay ve Diğer Özkaynağa Dayalı Araçların İhracından Kaynaklanan Nakit Girişleri": "Cash Inflows from Issue of Shares and Other Equity Instruments",
        "term.İşletmenin Kendi Paylarını ve Diğer Özkaynağa Dayalı Araçlarını Almasıyla İlgili Nakit Çıkışları": "Cash Outflows from Repurchase of Entity's Own Shares and Other Equity Instruments",
        "term.İşletmenin Kendi Paylarını ve Diğer Özkaynağa Dayalı Araçlarını Satmasından Kaynaklanan Nakit Girişleri": "Cash Inflows from Resale of Entity's Own Shares and Other Equity Instruments",
        "term.Borçlanmadan Kaynaklanan Nakit Girişleri": "Cash Inflows from Borrowings",
        "term.Borç Ödemelerine İlişkin Nakit Çıkışları": "Cash Outflows for Repayment of Borrowings",
        "term.Kira Sözleşmelerinden Kaynaklanan Borç Ödemelerine İlişkin Nakit Çıkışları": "Cash Outflows from Payments of Lease Liabilities",
        "term.İlişkili Taraflardan Alınan Diğer Borçlardaki Artış": "Increase in Other Borrowings from Related Parties",
        "term.İlişkili Taraflardan Alınan Diğer Borçlardaki Azalış": "Decrease in Other Borrowings from Related Parties",
        "term.Ödenen Faiz": "Interest Paid",
        "term.Yabancı Para Çevrim Farklarının Etkisinden Önce Nakit ve Nakit Benzerlerindeki Net Artış (Azalış)": "Net Increase (Decrease) in Cash and Cash Equivalents Before Effect of Exchange Rate Changes",
        "term.Yabancı Para Çevrim Farklarının Nakit ve Nakit Benzerleri Üzerindeki Etkisi": "Effect of Exchange Rate Changes on Cash and Cash Equivalents",
        "term.Nakit ve Nakit Benzerlerindeki Net Artış (Azalış)": "Net Increase (Decrease) in Cash and Cash Equivalents",
        "term.Dönem Başı Nakit ve Nakit Benzerleri": "Cash and Cash Equivalents at Beginning of Period",
        "term.Dönem Sonu Nakit ve Nakit Benzerleri": "Cash and Cash Equivalents at End of Period",
        "term.Türev Araçlardan Nakit Girişleri": "Cash Inflows from Derivative Instruments",
        "term.Türev Araçlardan Nakit Çıkışları": "Cash Outflows for Derivative Instruments",
        "term.Bağlı Ortaklıklarda İlave Pay Alımlarına ilişkin Nakit Çıkışları": "Cash Outflows for Acquisition of Additional Shares in Subsidiaries",
        "term.Başka İşletmelerin veya Fonların Paylarının veya Borçlanma Araçlarının Satılması Sonucu Elde Edilen Nakit Girişleri": "Cash Inflows from Sale of Shares or Debt Instruments of Other Entities or Funds",
        "term.Başka İşletmelerin veya Fonların Paylarının veya Borçlanma Araçlarının Edinimi İçin Yapılan Nakit Çıkışları": "Cash Outflows for Purchase of Shares or Debt Instruments of Other Entities or Funds",
        "term.Türev Yükümlülüklerdeki Artış (Azalış)": "Increase (Decrease) in Derivative Liabilities",
        "term.Türev Varlıklardaki Azalış (Artış)": "Decrease (Increase) in Derivative Assets",
        "term.Pazarlıklı Satın Alım Sonucu Oluşan Kazanç ile İlgili Düzeltmeler": "Adjustments for Gains on Bargain Purchase",
        "term.İtfa Edilmiş Maliyetinden Ölçülen Finansal Varlıkların Finansal Tablo Dışı Bırakılmasından Kaynaklanan Kazançlar (Kayıplar)": "Gains (Losses) from Derecognition of Financial Assets Measured at Amortized Cost",

        # Banking & Detailed Financial Items
        "term.Bilanço Kalemleri": "Balance Sheet Items",
        "term.FİNANSAL VARLIKLAR (Net)": "FINANCIAL ASSETS (Net)",
        "term.Gerçeğe Uygun Değer Farkı Kâr Zarara Yansıtılan Finansal Varlıklar": "Financial Assets at Fair Value Through Profit or Loss",
        "term.Gerçeğe Uygun Değer Farkı Diğer Kapsamlı Gelire Yansıtılan Finansal Varlıklar": "Financial Assets at Fair Value Through Other Comprehensive Income",
        "term.İtfa Edilmiş Maliyeti ile Ölçülen Finansal Varlıklar": "Financial Assets Measured at Amortized Cost",
        "term.Türev Finansal Varlıklar": "Derivative Financial Assets",
        "term.Donuk Finansal Varlıklar": "Non-Performing Financial Assets",
        "term.Beklenen Zarar Karşılıkları (-)": "Expected Credit Loss Provisions (-)",
        "term.KREDİLER (Net)": "LOANS (Net)",
        "term.Krediler": "Loans",
        "term.Kiralama İşlemlerinden Alacaklar": "Receivables from Leasing Transactions",
        "term.Faktoring Alacakları": "Factoring Receivables",
        "term.Donuk Alacaklar": "Non-Performing Receivables",
        "term.SATIŞ AMAÇLI ELDE TUTULAN VE DURDURULAN FAALİYETLERE İLİŞKİN DURAN VARLIKLAR (Net)": "NON-CURRENT ASSETS HELD FOR SALE AND DISCONTINUED OPERATIONS (Net)",
        "term.ORTAKLIK YATIRIMLARI": "INVESTMENTS IN ASSOCIATES AND JOINT VENTURES",
        "term.İştirakler (Net)": "Associates (Net)",
        "term.Bağlı Ortaklıklar (Net)": "Subsidiaries (Net)",
        "term.Birlikte Kontrol Edilen Ortaklıklar (İş Ortaklıkları) (Net)": "Jointly Controlled Entities (Joint Ventures) (Net)",
        "term.MADDİ DURAN VARLIKLAR (Net)": "PROPERTY, PLANT AND EQUIPMENT (Net)",
        "term.Maddi Olmayan Duran Varlıklar (Net)": "Intangible Assets (Net)",
        "term.Yatırım Amaçlı Gayrimenkuller (Net)": "Investment Properties (Net)",
        "term.Cari Vergi Varlığı": "Current Tax Asset",
        "term.Diğer Aktifler": "Other Assets",
        "term.VARLIKLAR TOPLAMI": "TOTAL ASSETS",
        "term.Mevduat": "Deposits",
        "term.Alınan Krediler": "Loans Received",
        "term.Para Piyasasına Borçlar": "Payables to Money Markets",
        "term.İhraç Edilen Menkul Kıymetler (Net)": "Securities Issued (Net)",
        "term.Bonolar": "Bills",
        "term.Varlığa Dayalı Menkul Kıymetler": "Asset-Backed Securities",
        "term.Tahviller": "Bonds",
        "term.Fonlar": "Funds",
        "term.Gerçeğe Uygun Değer Farkı Kar Zarara Yansıtılan Finansal Yükümlülükler": "Financial Liabilities at Fair Value Through Profit or Loss",
        "term.Türev Finansal Yükümlülükler": "Derivative Financial Liabilities",
        "term.Faktoring Yükümlülükleri": "Factoring Payables",
        "term.Kiralama İşlemlerinden Yükümlülükler": "Lease Liabilities",
        "term.Karşılıklar": "Provisions",
        "term.Cari Vergi Borcu": "Current Tax Liability",
        "term.Ertelenmiş Vergi Borcu": "Deferred Tax Liability",
        "term.Satış Amaçlı Elde Tutulan Ve Durdurulan Faaliyetlere İlişkin Duran Varlık Borçları (Net)": "Liabilities Associated with Non-Current Assets Held for Sale and Discontinued Operations (Net)",
        "term.Sermaye Benzeri Borçlanma Araçları": "Subordinated Debt Instruments",
        "term.Diğer Yükümlülükler": "Other Liabilities",
        "term.Sermaye Yedekleri": "Capital Reserves",
        "term.Kâr veya Zararda Yeniden Sınıflandırılmayacak Birikmiş Diğer Kapsamlı Gelirler veya Giderler": "Other Comprehensive Income or Expenses Not Reclassified to Profit or Loss",
        "term.Kâr veya Zararda Yeniden Sınıflandırılacak Birikmiş Diğer Kapsamlı Gelirler veya Giderler": "Other Comprehensive Income or Expenses Reclassified to Profit or Loss",
        "term.Kar Yedekleri": "Profit Reserves",
        "term.Kar veya Zarar": "Profit or Loss",
        "term.Geçmiş Yıllar Kar veya Zararı": "Prior Years' Profit or Loss",
        "term.Dönem Net Kâr veya Zararı": "Net Profit or Loss for the Period",
        "term.YÜKÜMLÜLÜKLER TOPLAMI": "TOTAL LIABILITIES",
        "term.Gelir Tablosu Kalemleri": "Income Statement Items",
        "term.FAİZ GELİRLERİ": "INTEREST INCOME",
        "term.Kredilerden Alınan Faizler": "Interest Received from Loans",
        "term.Zorunlu Karşılıklardan Alınan Faizler": "Interest Received from Reserve Requirements",
        "term.Bankalardan Alınan Faizler": "Interest Received from Banks",
        "term.Para Piyasası İşlemlerinden Alınan Faizler": "Interest Received from Money Market Transactions",
        "term.Menkul Değerlerden Alınan Faizler": "Interest Received from Securities",
        "term.Finansal Kiralama Gelirleri": "Finance Lease Income",
        "term.Diğer Faiz Gelirleri": "Other Interest Income",
        "term.FAİZ GİDERLERİ (-)": "INTEREST EXPENSES (-)",
        "term.Mevduata Verilen Faizler": "Interest Paid on Deposits",
        "term.Kullanılan Kredilere Verilen Faizler": "Interest Paid on Loans Used",
        "term.Para Piyasası İşlemlerine Verilen Faizler": "Interest Paid on Money Market Transactions",
        "term.İhraç Edilen Menkul Kıymetlere Verilen Faizler": "Interest Paid on Securities Issued",
        "term.Diğer Faiz Giderleri": "Other Interest Expenses",
        "term.NET FAİZ GELİRİ VEYA GİDERİ": "NET INTEREST INCOME OR EXPENSE",
        "term.NET ÜCRET VE KOMİSYON GELİRLERİ VEYA GİDERLERİ": "NET FEE AND COMMISSION INCOME OR EXPENSES",
        "term.Alınan Ücret ve Komisyonlar": "Fees and Commissions Received",
        "term.Verilen Ücret ve Komisyonlar (-)": "Fees and Commissions Paid (-)",
        "term.PERSONEL GİDERLERİ (-)": "PERSONNEL EXPENSES (-)",
        "term.TEMETTÜ GELİRLERİ": "DIVIDEND INCOME",
        "term.TİCARİ KAR VEYA ZARAR (Net)": "TRADING PROFIT OR LOSS (Net)",
        "term.Sermaye Piyasası İşlemleri Karı (Zararı)": "Profit (Loss) on Capital Market Operations",
        "term.Türev Finansal İşlemlerden Kar (Zarar)": "Profit (Loss) on Derivative Financial Transactions",
        "term.Kambiyo İşlemleri Karı (Zararı)": "Foreign Exchange Profit (Loss)",
        "term.FAALİYET BRÜT KÂRI": "GROSS OPERATING PROFIT",
        "term.NET FAALİYET KARI (ZARARI)": "NET OPERATING PROFIT (LOSS)",
        "term.Birleşme İşlemi Sonrasında Gelir Olarak Kaydedilen Fazlalık Tutarı": "Excess Amount Recorded as Income After Merger",
        "term.Özkaynak Yöntemi Uygulanan Ortaklıklardan Kar (Zarar)": "Profit (Loss) from Associates Accounted for Using Equity Method",
        "term.Net Parasal Pozisyon Karı (Zararı)": "Net Monetary Position Profit (Loss)",
        "term.Sürdürülen Faaliyetler Vergi Karşılığı (+/-)": "Tax Provision for Continuing Operations (+/-)",
        "term.Cari Vergi Karşılığı": "Current Tax Provision",
        "term.Ertelenmiş Vergi Gider Etkisi": "Deferred Tax Expense Effect",
        "term.Ertelenmiş Vergi Gelir Etkisi": "Deferred Tax Income Effect",
        "term.SÜRDÜRÜLEN FAALİYETLER DÖNEM NET KARI (ZARARI)": "NET PROFIT (LOSS) FOR THE PERIOD FROM CONTINUING OPERATIONS",
        "term.DÖNEM NET KARI VEYA ZARARI": "NET PROFIT OR LOSS FOR THE PERIOD",
        "term.Grubun Karı (Zararı)": "Group Profit (Loss)",
        "term.Azınlık Payları Karı (Zararı)": "Non-Controlling Interests Profit (Loss)",
        "term.Türev Araçlardan Nakit Girişleri": "Cash Inflows from Derivative Instruments",
        "term.Türev Araçlardan Nakit Çıkışları": "Cash Outflows for Derivative Instruments",
        "term.Bağlı Ortaklıklarda İlave Pay Alımlarına ilişkin Nakit Çıkışları": "Cash Outflows for Acquisition of Additional Shares in Subsidiaries",
        "term.Başka İşletmelerin veya Fonların Paylarının veya Borçlanma Araçlarının Satılması Sonucu Elde Edilen Nakit Girişleri": "Cash Inflows from Sale of Shares or Debt Instruments of Other Entities or Funds",
        "term.Başka İşletmelerin veya Fonların Paylarının veya Borçlanma Araçlarının Edinimi İçin Yapılan Nakit Çıkışları": "Cash Outflows for Purchase of Shares or Debt Instruments of Other Entities or Funds",
        "term.Türev Yükümlülüklerdeki Artış (Azalış)": "Increase (Decrease) in Derivative Liabilities",
        "term.Türev Varlıklardaki Azalış (Artış)": "Decrease (Increase) in Derivative Assets",
        "term.Pazarlıklı Satın Alım Sonucu Oluşan Kazanç ile İlgili Düzeltmeler": "Adjustments for Gains on Bargain Purchase",
        "term.İtfa Edilmiş Maliyetinden Ölçülen Finansal Varlıkların Finansal Tablo Dışı Bırakılmasından Kaynaklanan Kazançlar (Kayıplar)": "Gains (Losses) from Derecognition of Financial Assets Measured at Amortized Cost",
        "term.Finans Sektörü Faaliyetlerinden Alacaklar": "Receivables from Financial Sector Operations",
        "term.Diğer Finansal Yükümlülükler": "Other Financial Liabilities",
        "term.Finans Sektörü Faaliyetlerinden Borçlar": "Payables from Financial Sector Operations",
        "term.Satış Amaçlı Sınıflandırılan Varlık Gruplarına İlişkin Yükümlülükler": "Liabilities Associated with Asset Groups Classified as Held for Sale",
        "term.Özkaynak Yöntemiyle Değerlenen Yatırımlardan Yükümlülükler": "Liabilities from Investments Accounted for Using Equity Method",
        "term.Faiz, Ücret, Prim, Komisyon ve Diğer Gelirler": "Interest, Fee, Premium, Commission and Other Income",
        "term.Finans Sektörü Faaliyetlerinden Brüt Kar (Zarar)": "Gross Profit (Loss) from Financial Sector Operations",
        "term.Durdurulan Faaliyetler Dönem Karı/Zararı": "Profit (Loss) for the Period from Discontinued Operations",
        "term.Nakit Dışı Kalemlere İlişkin Diğer Düzeltmeler": "Other Adjustments for Non-Cash Items",
        "term.İştirak, İş ortaklığı ve Finansal Yatırımların Elden Çıkarılmasından veya Paylarındaki Değişim Sebebi ile Oluşan Kayıplar (Kazançlar) ile İlgili Düzeltmeler": "Adjustments for Losses (Gains) on Disposal of or Changes in Shares of Associates, Joint Ventures and Financial Investments",
        "term.Bağlı Ortaklıkların veya Müşterek Faaliyetlerin Elden Çıkarılmasından Kaynaklanan Kayıplar (Kazançlar) ile İlgili Düzeltmeler": "Adjustments for Losses (Gains) on Disposal of Subsidiaries or Joint Operations",
        "term.Durdurulan Faaliyetlere İlişkin Net Nakit Akışları": "Net Cash Flows from Discontinued Operations",
        "term.Bağlı Ortaklıklardaki Kontrolün Kaybına Yol Açmayan Şekilde Ortaklık Payları Değişmelerinden Kaynaklanan Nakit Çıkışları": "Cash Outflows from Changes in Ownership Interests in Subsidiaries that do not Result in Loss of Control",
        "term.Devlet Teşvik ve Yardımları": "Government Grants and Assistance",
        "term.Diğer Kazançlar (Kayıplar)": "Other Gains (Losses)",
        "term.Devlet Teşviklerinden Elde Edilen Gelirler ile İlgili Düzeltmeler": "Adjustments for Income from Government Grants",
        "term.Devlet Teşvik ve Yardımlarındaki Artış (Azalış)": "Increase (Decrease) in Government Grants and Assistance",
        "term.Diğer Özkaynak Payları": "Other Equity Interests",
        "term.Katılım (Kar) Payı ve Diğer Finansal Araçlardan Nakit Çıkışları": "Cash Outflows from Profit Share and Other Financial Instruments",
        "term.Katılım (Kar) Payı ve Diğer Finansal Araçlardan Nakit Girişleri": "Cash Inflows from Profit Share and Other Financial Instruments",
        "term.Bağlı Ortaklıkların Kontrolünün Kaybı Sonucunu Doğurmayan Satışlara İlişkin Nakit Girişleri": "Cash Inflows from Sales of Subsidiaries that do not Result in Loss of Control",
        "term.Katılım (Kar) Payı ve Diğer Finansal Araçlardan (Gelirler) Giderler ile İlgili Düzeltmeler": "Adjustments for (Income) Expenses from Profit Share and Other Financial Instruments",
        "term.Gayrimenkul Projeleri Kapsamında Açılan Nakit Hesapları": "Cash Accounts Opened Under Real Estate Projects",
        "term.Pay Bazlı Ödemeler İle İlgili Düzeltmeler": "Adjustments for Share-Based Payments",
        "term.İştiraklerin ve/veya İş Ortaklıklarının Pay Satışı veya Sermaye Azaltımı Sebebiyle Oluşan Nakit Girişleri": "Cash Inflows from Sale of Shares or Capital Reduction of Associates and/or Joint Ventures",
        "term.Satış Amacıyla Elde Tutulan Duran Varlık Alımlarından Nakit Çıkışları": "Cash Outflows from Purchase of Non-Current Assets Held for Sale",
        "term.Bağlı Ortaklıkların Kontrolünün Kaybı Sonucunu Doğuracak Satışlara İlişkin Nakit Girişleri": "Cash Inflows from Sales of Subsidiaries that Result in Loss of Control",
        "term.İştirakler, İş Ortaklıkları ve/veya Müşterek Faaliyetlerin Sermaye Artırımına Katılımdan Kaynaklanan Nakit Çıkışları": "Cash Outflows from Participation in Capital Increase of Associates, Joint Ventures and/or Joint Operations",
        "term.Takas İşlemlerinden Kaynaklanan Kayıplar (Kazançlar) ile İlgili Düzeltmeler": "Adjustments for Losses (Gains) from Exchange Transactions",
        "term.Faiz, Ücret, Prim, Komisyon ve Diğer Giderler (-)": "Interest, Fee, Premium, Commission and Other Expenses (-)",
        "term.Türkiye Cumhuriyet Merkez Bankası Hesabı": "Central Bank of the Republic of Turkey Account",
        "term.Ödenen Kar Payı Avansları (Net) (-)": "Dividend Advances Paid (Net) (-)",
        "term.Birleşme Denkleştirme Hesabı": "Merger Equalization Account",
        "term.Müşteri Sözleşmelerinden Doğan Varlıklardaki Azalış (Artış) İle İlgili Düzeltmeler": "Adjustments for Decrease (Increase) in Assets from Customer Contracts",
        "term.Cari Dönem Vergisiyle İlgili Borçlar": "Current Income Tax Liabilities",
        "term.Cari Dönem Vergisiyle İlgili Duran Varlıklar": "Current Income Tax Assets (Non-Current)",
        
        # Fund Asset Types
        "term.Finansman Bonosu": "Commercial Paper",
        "term.Hisse Senedi": "Equities",
        "term.Özel Sektör Kira Sert.": "Private Sector Lease Certificates",
        "term.Repo": "Repo",
        "term.Ters-Repo": "Reverse Repo",
        "term.Vadeli İşlemler Nakit Teminatları": "Derivatives Cash Margins",
        "term.Mevduat (TL)": "Deposits (TRY)",
        "term.Mevduat (Döviz)": "Deposits (FX)",
        "term.Yatırım Fonları Katılma Payları": "Mutual Fund Shares",
        "term.Girişim S. YF Kat. Payları": "Venture Capital Fund Shares",
        "term.Kıymetli Madenler": "Precious Metals",
        "term.Devlet Tahvili": "Government Bonds",
        "term.Kıymetli Maden Cinsinden BYF": "Precious Metals ETFs",
        "term.Diğer": "Other",
        "term.Takasbank Para Piyasası": "Takasbank Money Market",
        "term.Yabancı BYF": "Foreign ETFs",
        "term.BYF Katılma Payları": "ETF Participation Certificates",
        "term.Katılma Hesabı (TL)": "Participation Account (TRY)",
        "term.BİST Taahhütlü İşlem Pazarı Satım": "BIST Commitment Market Sell",
        "term.Yabancı Hisse Senedi": "Foreign Equities",
        
        "term.Likidite Oranları": "Liquidity Ratios",
        "term.Kaldıraç Oranları": "Leverage Ratios",
        "term.Faaliyet Etkinlik Oranları": "Activity / Efficiency Ratios",
        "term.Karlılık Oranları": "Profitability Ratios",
        "term.Diğer Kalemler": "Other Items",
        "term.Cari Oran": "Current Ratio",
        "term.Likidite Oranı": "Quick Ratio",
        "term.Nakit Oran": "Cash Ratio",
        "term.Finansal Borç Oranı": "Financial Debt Ratio",
        "term.Kaldıraç Oranı": "Leverage Ratio",
        "term.Aktif Devir Hızı": "Asset Turnover",
        "term.Stok Devir Hızı": "Inventory Turnover",
        "term.Alacak Devir Hızı": "Receivables Turnover",
        "term.Özkaynak Devir Hızı": "Equity Turnover",
        "term.Borç Devir Hızı": "Payables Turnover",
        "term.Aktif Karlılık": "Return on Assets (ROA)",
        "term.Özkaynak Karlılığı": "Return on Equity (ROE)",
        "term.Brüt Kar Marjı": "Gross Margin",
        "term.Esas Faaliyet Kar Marjı": "Operating Margin",
        "term.FAVÖK Marjı": "EBITDA Margin",
        "term.Net Kar Marjı": "Net Profit Margin",
        "term.Brüt Kar Marjı (Çeyreklik)": "Gross Margin (Quarterly)",
        "term.Esas Faaliyet Kar Marjı (Çeyreklik)": "Operating Margin (Quarterly)",
        "term.FAVÖK Marjı (Çeyreklik)": "EBITDA Margin (Quarterly)",
        "term.Net Kar Marjı (Çeyreklik)": "Net Profit Margin (Quarterly)",
        "term.Satışlar (Çeyreklik)": "Sales (Quarterly)",
        "term.FAVÖK (Çeyreklik)": "EBITDA (Quarterly)",
        "term.Net Faaliyet Karı (Çeyreklik)": "Net Operating Profit (Quarterly)",
        "term.Net Kar (Çeyreklik)": "Net Profit (Quarterly)",
        "term.Satışlar (Yıllıklandırılmış)": "Sales (Annualized)",
        "term.FAVÖK (Yıllıklandırılmış)": "EBITDA (Annualized)",
        "term.Net Faaliyet Karı (Yıllıklandırılmış)": "Net Operating Profit (Annualized)",
        "term.Net Kar (Yıllıklandırılmış)": "Net Profit (Annualized)",
        "term.Çeyreklik Serbest Nakit Akışı": "Quarterly Free Cash Flow",
        "term.Yıllıklandırılmış Serbest Nakit Akışı": "Annualized Free Cash Flow",
    },

    "tr": {
        # Common / Errors
        "error.prefix": "[bold red]Hata:[/bold red]",
        "error.unknown_subcommand": "Bilinmeyen alt komut: '{subcommand}'. Desteklenenler: {supported}",
        "error.auth_required": "Bu işlem için kimlik doğrulama gereklidir. Lütfen .env dosyasında FINTABLES_USERNAME veya FINTABLES_EMAIL ve FINTABLES_PASSWORD değerlerini ayarlayın.",
        "error.session_expired": "Oturum süresi doldu veya kimlik doğrulama başarısız oldu.",
        "error.not_found": "İstenen kaynak bulunamadı (404): {url}",
        "error.api_error": "API hatası ({status}): {detail}",
        "error.login_request_failed": "Giriş isteği sırasında hata oluştu: {error}",
        "error.login_failed": "Giriş yapılamadı: {detail}. Lütfen FINTABLES_USERNAME/FINTABLES_EMAIL ve FINTABLES_PASSWORD ayarlarınızı kontrol edin.",
        "error.refresh_failed": "Token yenileme sırasında hata oluştu: {error}",
        "error.refresh_unsuccessful": "Token yenilenemedi. Lütfen tekrar giriş yapın.",
        "common.yes": "Evet",
        "common.no": "Hayır",

        # CLI App & Callbacks
        "cli.app.help": "Fintables Mobil API İstemcisi ve CLI Aracı",
        "cli.app.version_help": "Fintables sürümünü gösterir",
        "cli.app.lang_help": "Dil seçimi (en, tr)",

        # CLI Top-level Command Descriptions
        "cli.cmd.company": "Şirket profili ve oran tiplerini getirir",
        "cli.cmd.symbol": "Hisse özeti veya finansal tabloları (sheets) getirir",
        "cli.cmd.analyst": "Analist beklentileri ve hedef fiyatlarını getirir",
        "cli.cmd.search": "Hisse, vadeli ve varant araması yapar",
        "cli.cmd.feed": "Haber ve KAP akışını getirir",
        "cli.cmd.fund": "Yatırım fonu detayları ve portföy dağılımını getirir",
        "cli.cmd.agenda": "Ekonomik takvim ve temettü ajandasını getirir",
        "cli.cmd.watchlist": "Favori hisse listesini yönetir",
        "cli.cmd.memo": "Hisselere eklenen notları yönetir (ekle, listele, güncelle, sil)",
        "cli.cmd.auth": "Kimlik doğrulama işlemleri",
        "cli.cmd.portfolio": "Sanal portföy yönetimi",
        "cli.cmd.newsletter": "Fintables bültenleri",
        "cli.cmd.post": "Fintables araştırma yazıları ve şirket notları",
        "cli.cmd.video": "Fintables YouTube ve borsa videoları",
        "cli.cmd.notification": "Fintables bildirimlerini görüntüler ve yönetir",
        "cli.cmd.shell": "İnteraktif REPL kabuk oturumunu başlatır",

        # CLI Shared Options & Arguments
        "cli.common.output_help": "Çıktı formatı: table veya json",
        "cli.common.ticker_help": "Hisse kodu (örn. ASELS, FROTO)",

        # CLI: Symbol
        "cli.symbol.subcommand_help": "Alt komut: summary veya sheets",
        "cli.symbol.sheet_help": "Görüntülenecek tablo: balance, income, cashflow veya all",
        "cli.symbol.periods_help": "Görüntülenecek dönem sayısı",
        "cli.symbol.quarterly_help": "Kümülatif yerine çeyreklik verileri göster",

        # CLI: Analyst
        "cli.analyst.brokerage_help": "Belirli bir aracı kuruma göre filtrele (örn. PHC, IYM)",
        "cli.analyst.model_portfolio_help": "Yalnızca model portföydeki aracı kurumları göster",

        # CLI: Search
        "cli.search.query_help": "Aranacak kelime (örn. ASELS, SASA, Polyester)",

        # CLI: Feed
        "cli.feed.ticker_help": "Filtrelenecek hisse kodu (örn. FROTO). Belirtilmezse genel akış çekilir.",
        "cli.feed.type_help": "İçerik türü filtresi: post, news, newsletter, article",
        "cli.feed.importance_help": "Önem derecesi filtresi: low, mid, high",
        "cli.feed.page_size_help": "Sayfa başına haber sayısı",
        "cli.feed.cursor_help": "Sayfalama imleci (sonraki sayfalar için)",

        # CLI: Fund
        "cli.fund.ticker_help": "Fon kodu (örn. TLY, MAC)",

        # CLI: Agenda
        "cli.agenda.time_help": "Zaman aralığı: today | thisWeek | nextWeek",
        "cli.agenda.type_help": "Tür filtresi: dividend | macro",
        "cli.agenda.invalid_time": "Geçersiz zaman aralığı: '{time}'. Seçenekler: {options}",

        # CLI: Watchlist
        "cli.watchlist.add_help": "Bir hisseyi favorilere ekler.",
        "cli.watchlist.remove_help": "Bir hisseyi favorilerden çıkarır.",

        # CLI: Memo
        "cli.memo.list_help": "Kayıtlı tüm notları listeler.",
        "cli.memo.add_help": "Bir hisseye yeni not ekler.",
        "cli.memo.update_help": "Mevcut bir notu günceller.",
        "cli.memo.delete_help": "Bir notu siler.",
        "cli.memo.code_help": "Hisse kodu (örn. FROTO)",
        "cli.memo.content_help": "Not içeriği",
        "cli.memo.id_help": "Not ID",

        # CLI: Auth
        "cli.auth.login_help": "Bağlantıyı test etmek için e-posta ve şifre ile giriş yapar.",
        "cli.auth.email_help": "Fintables e-posta adresi",
        "cli.auth.username_help": "Fintables kullanıcı adı / e-posta",
        "cli.auth.password_help": "Fintables şifresi",
        "cli.auth.missing_credentials": "E-posta veya şifre girilmedi. Lütfen argüman olarak verin ya da .env dosyanızda FINTABLES_EMAIL / FINTABLES_USERNAME ve FINTABLES_PASSWORD tanımlayın.",
        "cli.auth.login_success": "✅ Giriş başarılı!",
        "cli.auth.access_token": "Erişim Belirteci: [dim]{token}...[/dim]",

        # CLI: Portfolio
        "cli.portfolio.list_help": "Sanal portföyleri listeler.",
        "cli.portfolio.create_help": "Yeni bir sanal portföy oluşturur.",
        "cli.portfolio.delete_help": "Bir sanal portföyü siler.",
        "cli.portfolio.rename_help": "Portföy adını değiştirir.",
        "cli.portfolio.show_help": "Portföydeki pozisyonları gösterir.",
        "cli.portfolio.buy_help": "Portföye alış işlemi ekler.",
        "cli.portfolio.sell_help": "Portföye satış işlemi ekler.",
        "cli.portfolio.name_or_uuid_help": "Portföy adı veya UUID",
        "cli.portfolio.create_title_help": "Portföy adı",
        "cli.portfolio.rename_title_help": "Yeni portföy adı",
        "cli.portfolio.ticker_help": "Hisse sembolü (örn. SASA)",
        "cli.portfolio.amount_help": "Adet",
        "cli.portfolio.price_help": "Alış fiyatı",
        "cli.portfolio.sell_price_help": "Satış fiyatı",
        "cli.portfolio.date_help": "İşlem tarihi (YYYY-AA-GG)",
        "cli.portfolio.not_found": "Portföy bulunamadı: '{identifier}'",
        "cli.portfolio.multiple_found": "'{identifier}' adında birden fazla portföy bulundu. Lütfen UUID kullanın.",
        "cli.portfolio.empty": "Henüz portföy bulunamadı.",
        "cli.portfolio.created": "✅ Portföy oluşturuldu: [bold cyan]{title}[/bold cyan] [dim]({id})[/dim]",
        "cli.portfolio.deleted": "✅ Portföy silindi: [bold cyan]{identifier}[/bold cyan]",
        "cli.portfolio.renamed": "✅ Portföy adı güncellendi: [bold cyan]{old_title}[/bold cyan] → [bold green]{new_title}[/bold green]",
        "cli.portfolio.buy_success": "✅ Alış işlemi eklendi: {portfolio} | {ticker} | {amount} @ {price}",
        "cli.portfolio.sell_success": "✅ Satış işlemi eklendi: {portfolio} | {ticker} | {amount} @ {price}",
        "cli.portfolio.positions_empty": "Portföyde pozisyon bulunamadı. ({title})",
        "cli.portfolio.table_title": "Portföyler",
        "cli.portfolio.col_id": "ID / UUID",
        "cli.portfolio.col_title": "Portföy Adı",
        "cli.portfolio.pos_title": "Portföy: {title}",
        "cli.portfolio.col_stock": "Hisse",
        "cli.portfolio.col_quantity": "Adet",
        "cli.portfolio.col_avg_cost": "Maliyet",
        "cli.portfolio.col_current_price": "Fiyat",
        "cli.portfolio.col_total_value": "Tutar",
        "cli.portfolio.col_return_pct": "Getiri %",
        "cli.portfolio.col_total_cost": "Toplam Maliyet",
        "cli.portfolio.col_gain_loss": "Kâr/Zarar",
        "cli.portfolio.col_gain_loss_pct": "Kâr/Zarar %",
        "cli.portfolio.available_portfolios": "Mevcut portföyler: {names}",
        "cli.portfolio.use_uuid": "Lütfen doğrudan UUID kullanın: {ids}",
        "cli.portfolio.total_row": "TOPLAM",

        # CLI: Newsletter
        "cli.newsletter.list_help": "Bültenleri listeler.",
        "cli.newsletter.read_help": "Bülten içeriğini okur.",
        "cli.newsletter.category_help": "Kategori filtresi",
        "cli.newsletter.page_help": "Sayfa numarası",
        "cli.newsletter.slug_help": "Bülten slug'ı (örn. bulten-123)",

        # CLI: Post
        "cli.post.list_help": "Araştırma yazılarını ve şirket notlarını listeler.",
        "cli.post.read_help": "Yazı içeriğini okur (içerik + benzer yazılar).",
        "cli.post.category_help": "Kategori filtresi",
        "cli.post.page_help": "Sayfa numarası",
        "cli.post.slug_help": "Yazı slug'ı (örn. sasa-analiz)",

        # CLI: Video
        "cli.video.list_help": "Videoları listeler.",
        "cli.video.show_help": "Video detaylarını, açıklamasını ve YouTube bağlantısını gösterir.",
        "cli.video.type_help": "İçerik türü (örn. video)",
        "cli.video.filter_help": "Başlık veya seri içinde ara",
        "cli.video.series_help": "Seri filtresi",
        "cli.video.page_help": "Sayfa numarası",
        "cli.video.slug_help": "Video slug'ı",

        # CLI: Notification
        "cli.notification.list_help": "Bildirimleri listeler.",
        "cli.notification.unread_help": "Okunmamış bildirim durumunu ve son okuma tarihini görüntüler.",
        "cli.notification.status_help": "Okunmamış bildirim durumunu ve son okuma tarihini görüntüler (unread takma adı).",
        "cli.notification.mark_read_help": "Tüm bildirimleri okundu olarak işaretler.",
        "cli.notification.page_size_help": "Getirilecek bildirim sayısı (varsayılan: 100)",

        # Formatter / Output: Company & Symbol
        "output.inflation_accounting": "Enflasyon Muhasebesi",
        "output.participation_index": "Katılım Endeksi",
        "output.col_category": "Kategori",
        "output.col_ratio": "Oran",
        "output.col_access": "Erişim",
        "output.ratio_types": "Oran Tipleri:",
        "output.col_code": "Kod",
        "output.col_title": "Başlık",
        "output.col_group": "Grup",
        "output.col_item": "Kalem",
        "output.col_value": "Değer",
        "output.col_period": "Periyot",
        "output.col_yield": "Getiri",
        "output.col_initial": "İlk",
        "output.col_low": "Düşük",
        "output.col_high": "Yüksek",
        "output.period_1w": "1 Hafta",
        "output.col_brokerage": "Kurum",
        "output.col_portfolio": "Portföy",
        "output.col_importance": "Önem",
        "output.col_company": "Şirket",
        "output.feed_general": "Genel ",
        "output.feed_importance_high": "[bold red]●●● YÜKSEK[/bold red]",
        "output.feed_importance_mid": "[bold yellow]●○○ ORTA [/bold yellow]",
        "output.feed_importance_low": "[dim green]○○○ DÜŞÜK [/dim green]",
        "output.watchlist_empty": "(boş)",
        "output.search_group_stocks": "Hisseler",
        "output.search_group_futures": "Vadeli İşlemler",
        "output.search_group_warrants": "Varantlar",
        "output.search_group_other": "Diğer",
        "output.search_group_n": "Grup {n}",
        "output.search_results_found": "({found} sonuç)",
        "output.search_results_first": "({found} sonuç, ilk {shown} tanesi)",
        "output.col_symbol": "Sembol",
        "output.col_content": "İçerik",
        "output.col_updated": "Güncellendi",
        "output.col_stock": "Hisse",
        "output.col_weight": "Ağırlık",
        "output.col_nominal": "Nominal",
        "output.sheet_cash_flow": "Nakit Akım",

        # Formatter / Output: Analyst Ratings
        "output.analyst_ratings_header": "{ticker} — Analist Beklentileri ({count} kurum)",
        "output.col_institution": "Kurum",
        "output.col_target_price": "Hedef Fiyat",
        "output.col_upside": "Potansiyel",
        "output.col_rating": "Tavsiye",
        "output.min_target": "Min Hedef:",
        "output.avg_target": "Ort Hedef:",
        "output.max_target": "Maks Hedef:",
        "output.badge_buy": "AL",
        "output.badge_hold": "TUT",
        "output.badge_sell": "SAT",
        "output.badge_outperform": "ENDEKS ÜSTÜ GETİRİ",
        "output.badge_market_perform": "ENDEKSE PARALEL GETİRİ",
        "output.badge_underperform": "ENDEKS ALTI GETİRİ",

        # Formatter / Output: Sheets
        "output.sheet_balance": "Bilanço",
        "output.sheet_income": "Gelir Tablosu",
        "output.sheet_cashflow": "Nakit Akım Tablosu",
        "output.sheet_quarterly": "Çeyreklik",
        "output.sheet_cumulative": "Kümülatif",
        "output.inflation_note": "ℹ️  Veriler enflasyon düzeltmesi yapılmış ve konsolidedir.",

        # Formatter / Output: Feed
        "output.feed_header": "{ticker}Haber Akışı ({count} haber)",
        "output.col_date": "Tarih",
        "output.col_time": "Saat",
        "output.col_type": "Tür",
        "output.col_related": "İlgili",
        "output.next_page_note": "ℹ️  Sonraki sayfa mevcut. (--page-size ile artırabilirsiniz)",

        # Formatter / Output: Watchlist
        "output.watchlist_added": "✅  {ticker} favorilere eklendi.",
        "output.watchlist_removed": "🗑️  {ticker} favorilerden çıkarıldı.",
        "output.watchlist_label": "Favoriler: {items}",

        # Formatter / Output: Search
        "output.search_header": 'Arama: "{query}"',
        "output.search_no_results": "(Sonuç bulunamadı)",

        # Formatter / Output: Memos
        "output.memos_header": "Notlarınız ({count} not)",
        "output.col_stock": "Hisse",
        "output.col_note": "Not",
        "output.memo_added": "✅  Not eklendi (ID: {id})",
        "output.memo_updated": "✅  Not güncellendi (ID: {id})",
        "output.memo_deleted": "🗑️  Not silindi (ID: {id})",

        # Formatter / Output: Funds
        "output.fund_manager": "Yönetici:",
        "output.fund_price": "Fiyat:",
        "output.fund_risk": "Risk:",
        "output.fund_asset_allocation": "Varlık Dağılımı ({date})",
        "output.fund_asset_type": "Varlık Türü",
        "output.fund_ratio": "Oran",
        "output.fund_portfolio_breakdown": "Portföy Dağılımı ({date})",
        "output.fund_weight": "Ağırlık",
        "output.fund_nominal": "Nominal",
        "output.fund_yield_analysis": "Getiri Analizi",
        "output.fund_1m": "1 Ay",
        "output.fund_3m": "3 Ay",
        "output.fund_6m": "6 Ay",
        "output.fund_1y": "1 Yıl",
        "output.fund_3y": "3 Yıl",
        "output.fund_5y": "5 Yıl",
        "output.fund_ytd": "Yıl Başı (YTD)",

        # Formatter / Output: Agenda
        "output.agenda_empty": "Bu dönem için ajanda bulunamadı ({time_label}).",
        "output.agenda_today": "Bugün",
        "output.agenda_this_week": "Bu Hafta",
        "output.agenda_next_week": "Gelecek Hafta",
        "output.agenda_header": "Ajanda — {header} ({count} etkinlik)",
        "output.agenda_col_country": "Ülke/Kaynak",
        "output.agenda_col_detail": "Detay",

        # Formatter / Output: Editor Blocks & Content
        "output.editor_image": "Görsel: {url}",
        "output.newsletters_header": "Bültenler ({total} sonuç{more})",
        "output.more_suffix": ", +{count} daha",
        "output.col_category": "Kategori",
        "output.col_author": "Yazar",
        "output.col_slug": "Slug",
        "output.next_page_nav": "ℹ️  Sonraki sayfa mevcut (--page ile ilerleyebilirsiniz)",
        "output.content_not_found": "(İçerik bulunamadı)",

        # Formatter / Output: Posts
        "output.posts_header": "Yazılar ({total} sonuç{more})",
        "output.col_read_time": "Okuma",
        "output.col_pdf": "PDF",
        "output.min_abbr": "{count} dk",
        "output.min_read": "{count} dk okuma",
        "output.similar_posts": "Benzer Yazılar",

        # Formatter / Output: Videos
        "output.videos_header": "Videolar ({total} sonuç{more})",
        "output.col_series": "Seri",
        "output.col_duration": "Süre",
        "output.col_youtube": "YouTube",
        "output.about_series": "Seri Hakkında: {desc}",
        "output.desc_and_chapters": "Açıklama & Bölümler",

        # Formatter / Output: Notifications
        "output.notifications_title": "Bildirimler",
        "output.notifications_empty": "Hiç bildirim bulunamadı.",
        "output.col_message": "Mesaj",
        "output.col_link": "Bağlantı",
        "output.notif_next_page": "ℹ️  Sonraki sayfa mevcut (--page-size ile artırabilirsiniz)",
        "output.notif_unread_badge": "🔴 Okunmamış bildirimleriniz var.",
        "output.notif_all_read_badge": "🟢 Tüm bildirimler okundu.",
        "output.notif_last_read_time": "Son okuma zamanı: {time}",
        "output.notif_last_read_none": "Son okuma zamanı: —",
        "output.notif_status_title": "Bildirim Durumu",
        "output.notif_mark_read_success": "✅ Tüm bildirimler okundu olarak işaretlendi.",
        "output.notif_action_status": "⚠️  İşlem durumu: {status}",
        "output.eligible": "Uygun",
        "output.not_eligible": "Uygun Değil",
    },
}


def _detect_system_language() -> str:
    """Detects system language from environment or locale."""
    for env_var in ("LC_ALL", "LC_MESSAGES", "LANG"):
        val = os.environ.get(env_var, "").lower()
        if val.startswith("tr"):
            return "tr"
        if val.startswith("en"):
            return "en"
    try:
        loc = locale.getlocale()[0]
        if loc and loc.lower().startswith("tr"):
            return "tr"
    except Exception:
        pass
    return "en"


def _check_argv_lang() -> str | None:
    """Checks sys.argv early for --lang or -l option."""
    for i, arg in enumerate(sys.argv):
        if arg in ("--lang", "-l") and i + 1 < len(sys.argv):
            val = sys.argv[i + 1].strip().lower()
            if val in TRANSLATIONS:
                return val
        elif arg.startswith("--lang="):
            val = arg.split("=", 1)[1].strip().lower()
            if val in TRANSLATIONS:
                return val
    return None


def get_language() -> str:
    """Returns the current active language code ('en', 'tr', etc.)."""
    global _current_language
    if _current_language:
        return _current_language

    # 1. Check CLI args early
    argv_lang = _check_argv_lang()
    if argv_lang:
        return argv_lang

    # 2. Check FINTABLES_LANG or FINTABLES_LANGUAGE
    env_lang = os.environ.get("FINTABLES_LANG") or os.environ.get("FINTABLES_LANGUAGE")
    if env_lang:
        code = env_lang.strip().lower()[:2]
        if code in TRANSLATIONS:
            return code

    # 3. Check settings.lang
    try:
        from fintables.config import settings
        if settings.lang:
            code = settings.lang.strip().lower()[:2]
            if code in TRANSLATIONS:
                return code
    except Exception:
        pass

    # 4. Check system locale
    sys_lang = _detect_system_language()
    if sys_lang in TRANSLATIONS:
        return sys_lang

    return "en"


_CLI_REGISTRY: list[tuple[object, str]] = []


def register_i18n(target: object, key: str) -> object:
    """Registers a Typer app, command, or parameter with an i18n translation key."""
    _CLI_REGISTRY.append((target, key))
    return target


def sync_cli_translations(lang: str | None = None) -> None:
    """Updates all registered CLI components (apps, commands, parameters) to current language."""
    if lang:
        # Set language directly to avoid circular call: set_language → sync_cli_translations
        global _current_language
        norm = lang.strip().lower()[:2]
        _current_language = norm if norm in TRANSLATIONS else "en"
    for target, key in _CLI_REGISTRY:
        val = t(key)
        info = getattr(target, "info", None)
        if info is not None and hasattr(info, "help"):
            setattr(info, "help", val)
        if hasattr(target, "help"):
            setattr(target, "help", val)


def set_language(lang: str) -> None:
    """Sets the active language code."""
    global _current_language
    norm = lang.strip().lower()[:2]
    if norm in TRANSLATIONS:
        _current_language = norm
    else:
        _current_language = "en"
    sync_cli_translations()


def t(key: str, **kwargs) -> str:
    """Translates key to current language, formatting with kwargs."""
    current = get_language()
    lang_dict = TRANSLATIONS.get(current, TRANSLATIONS["en"])
    template = lang_dict.get(key)
    if template is None:
        template = TRANSLATIONS["en"].get(key, key)

    if kwargs:
        try:
            return template.format(**kwargs)
        except Exception:
            return template
    return template


_LOWERCASE_TERM_MAP = None

def _get_lowercase_term_map(lang: str) -> dict:
    global _LOWERCASE_TERM_MAP
    if _LOWERCASE_TERM_MAP is None:
        _LOWERCASE_TERM_MAP = {}
        for k, v in TRANSLATIONS.get(lang, {}).items():
            if k.startswith("term."):
                # Custom lower for Turkish characters
                lk = k.replace("I", "ı").replace("İ", "i").lower()
                _LOWERCASE_TERM_MAP[lk] = v
    return _LOWERCASE_TERM_MAP

def t_term(term: str | None) -> str:
    """Translates common financial terms, section headers, or items if in English mode. Case-insensitive."""
    if not term:
        return ""
    
    term_str = str(term).strip()
    current = get_language()
    
    if current == "tr":
        # Keep Turkish values as they are, but capitalize first letters for consistency if they are all lowercase
        if term_str.islower():
            return term_str.title()
        return term_str

    lk_key = f"term.{term_str}".replace("I", "ı").replace("İ", "i").lower()
    term_map = _get_lowercase_term_map("en")
    
    if lk_key in term_map:
        return term_map[lk_key]
        
    # Fallback to standard t() if not in map, just in case
    key = f"term.{term_str}"
    translated = t(key)
    if translated != key:
        return translated
        
    # If not found, return Title Case version of the original term
    if term_str.islower():
        return term_str.title()
    return term_str
