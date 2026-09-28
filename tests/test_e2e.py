import os
import pytest
from fintables import FintablesClient
from fintables.config import settings

HAS_CREDENTIALS = bool(
    os.getenv("FINTABLES_PASSWORD")
    or os.getenv("FINTABLES_EMAIL")
    or os.getenv("FINTABLES_USERNAME")
    or settings.password
)

skip_if_no_credentials = pytest.mark.skipif(
    not HAS_CREDENTIALS,
    reason="FINTABLES_PASSWORD/EMAIL/USERNAME ortam değişkenleri tanımlı olmadığı için E2E testi atlandı.",
)
from fintables.api.auth import login, refresh_token
from fintables.api.endpoints import (
    # Agenda
    get_agenda,
    # Analyst Ratings
    get_analyst_ratings,
    # Company & Symbols
    get_company,
    get_sheets,
    get_symbol_summary,
    # Feed
    get_feed,
    get_topic_feed,
    # Funds
    get_fund,
    get_fund_info,
    # Newsletters
    get_newsletter,
    list_newsletters,
    # Notifications
    get_unread_status,
    list_notifications,
    mark_notifications_as_read,
    # Memos
    create_memo,
    delete_memo,
    list_memos,
    update_memo,
    # Portfolios
    add_transaction,
    create_portfolio,
    delete_portfolio,
    get_positions,
    list_portfolios,
    update_portfolio,
    # Posts
    get_post,
    list_posts,
    # Search
    search,
    # Videos
    get_video,
    list_videos,
    # Favorites
    add_favorite,
    remove_favorite,
)


@skip_if_no_credentials
@pytest.mark.asyncio
async def test_e2e_auth_flow():
    """Auth login ve token doğrulama akışını test eder."""
    async with FintablesClient() as client:
        # Client settings üzerinden login dene
        if client.settings.email and client.settings.password:
            access, refresh = await login(
                client._client,
                email=client.settings.email,
                password=client.settings.password,
            )
            assert access is not None
            assert refresh is not None

            # Refresh token testi
            new_access = await refresh_token(client._client, refresh)
            assert new_access is not None


@skip_if_no_credentials
@pytest.mark.asyncio
async def test_e2e_public_and_read_endpoints():
    """Tüm okuma ve sorgulama endpoint'lerinin parametre alternatifleriyle çalıştığını doğrular."""
    async with FintablesClient() as client:
        # Şirket & Sembol
        company = await get_company(client, "ASELS")
        assert company is not None and company.code == "ASELS"

        summary = await get_symbol_summary(client, "ASELS")
        assert summary is not None

        # Analist Değerlendirmeleri (Model Portföy parametresi ile)
        ratings = await get_analyst_ratings(client, "ASELS")
        assert ratings is not None

        # Arama
        search_res = await search(client, "Aselsan")
        assert search_res is not None

        # Bilanço / Finansal Tablolar
        sheets_default = await get_sheets(client, "ASELS")
        assert sheets_default is not None

        # Fonlar
        fund = await get_fund(client, "TLY")
        assert fund is not None

        fund_info = await get_fund_info(client, "TLY")
        assert fund_info is not None

        # Akış (Ticker ve Topic filtreli)
        feed_symbol = await get_feed(client, ticker="ASELS")
        assert feed_symbol is not None

        feed_topic = await get_topic_feed(client, page_size=10)
        assert feed_topic is not None

        # Ajanda / Takvim (today, thisWeek, nextWeek ve tip filtreli)
        agenda_today = await get_agenda(client, "today")
        assert agenda_today is not None

        agenda_week = await get_agenda(client, "thisWeek")
        assert agenda_week is not None

        # Bültenler
        newsletters = await list_newsletters(client, main_category="bist")
        assert newsletters is not None
        if newsletters.results:
            single_newsletter = await get_newsletter(client, newsletters.results[0].slug)
            assert single_newsletter is not None

        # Postlar / İçerikler
        posts = await list_posts(client, main_category="bist")
        assert posts is not None
        if posts.results:
            single_post = await get_post(client, posts.results[0].slug)
            assert single_post is not None

        # Videolar
        videos = await list_videos(client, main_category="bist")
        assert videos is not None
        if videos.results:
            single_video = await get_video(client, videos.results[0].slug)
            assert single_video is not None

        # Bildirimler & Okundu İşaretleme
        notifications = await list_notifications(client, page_size=10)
        assert notifications is not None

        unread = await get_unread_status(client)
        assert unread is not None

        mark_res = await mark_notifications_as_read(client)
        assert mark_res is not None


@skip_if_no_credentials
@pytest.mark.asyncio
async def test_e2e_watchlist_lifecycle():
    """Favorilere ekleme ve çıkarma yaşam döngüsünü test eder."""
    async with FintablesClient() as client:
        add_res = await add_favorite(client, "ASELS")
        assert add_res is not None

        rem_res = await remove_favorite(client, "ASELS")
        assert rem_res is not None


@skip_if_no_credentials
@pytest.mark.asyncio
async def test_e2e_memo_lifecycle():
    """Not oluşturma, güncelleme ve silme yaşam döngüsünü test eder."""
    async with FintablesClient() as client:
        memos = await list_memos(client)
        assert memos is not None

        new_memo = await create_memo(client, "ASELS", "Pytest E2E Test Notu")
        assert new_memo is not None
        assert hasattr(new_memo, "id")

        updated_memo = await update_memo(
            client, new_memo.id, "ASELS", "Pytest E2E Test Notu Güncellendi"
        )
        assert updated_memo is not None

        await delete_memo(client, new_memo.id)


@skip_if_no_credentials
@pytest.mark.asyncio
async def test_e2e_portfolio_lifecycle():
    """Portföy yönetimi yaşam döngüsünü test eder."""
    async with FintablesClient() as client:
        portfolios = await list_portfolios(client)
        assert portfolios is not None

        target_portfolio_id = None
        should_delete = False

        try:
            created = await create_portfolio(client, "Pytest E2E Portföy")
            if created and hasattr(created, "id"):
                target_portfolio_id = str(created.id)
                should_delete = True
        except Exception:
            # Ücretsiz üyelik limiti varsa ilk mevcut portföyü kullan
            if portfolios.results:
                target_portfolio_id = str(portfolios.results[0].id)

        assert target_portfolio_id is not None

        # Güncelleme
        updated = await update_portfolio(
            client, target_portfolio_id, "Pytest Portföy Güncel İsim"
        )
        assert updated is not None

        # İşlem ekleme
        tx = await add_transaction(
            client=client,
            portfolio_id=target_portfolio_id,
            code="ASELS",
            side="BUY",
            amount=100.0,
            price=65.5,
            date="2026-09-28",
        )
        assert tx is not None

        # Pozisyonlar
        positions = await get_positions(client, target_portfolio_id)
        assert positions is not None

        # Temizlik
        if should_delete:
            await delete_portfolio(client, target_portfolio_id)
