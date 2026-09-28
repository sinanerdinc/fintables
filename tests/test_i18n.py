import os
import pytest
from unittest.mock import patch
from typer.testing import CliRunner

from fintables.i18n import (
    TRANSLATIONS,
    _CLI_REGISTRY,
    get_language,
    register_i18n,
    set_language,
    sync_cli_translations,
    t,
    _detect_system_language,
)
from fintables.cli.main import app
from fintables.output.formatter import rating_type_badge, print_notification_status
from fintables.models.notification import NotificationUnreadStatus

runner = CliRunner()


@pytest.fixture(autouse=True)
def reset_lang():
    set_language("en")
    yield
    set_language("en")


def test_t_function_translations():
    set_language("en")
    assert t("common.yes") == "Yes"
    assert t("common.no") == "No"
    assert "Fintables" in t("cli.app.help")

    set_language("tr")
    assert t("common.yes") == "Evet"
    assert t("common.no") == "Hayır"
    assert "Fintables" in t("cli.app.help")


def test_t_formatting_kwargs():
    set_language("en")
    res_en = t("cli.portfolio.created", title="My Portfolio", id="abc-123")
    assert "My Portfolio" in res_en
    assert "abc-123" in res_en

    set_language("tr")
    res_tr = t("cli.portfolio.created", title="Portföyüm", id="abc-123")
    assert "Portföyüm" in res_tr
    assert "abc-123" in res_tr


def test_fallback_to_english_and_missing():
    set_language("tr")
    # Non-existent key returns key itself
    assert t("non.existent.key.xyz") == "non.existent.key.xyz"


def test_set_and_get_language():
    set_language("tr")
    assert get_language() == "tr"

    set_language("en")
    assert get_language() == "en"

    # Unsupported language defaults to English
    set_language("fr")
    assert get_language() == "en"


def test_detect_system_language():
    with patch.dict(os.environ, {"LANG": "tr_TR.UTF-8"}):
        assert _detect_system_language() == "tr"

    with patch.dict(os.environ, {"LANG": "en_US.UTF-8"}):
        assert _detect_system_language() == "en"


def test_formatter_badges_localized():
    set_language("en")
    badge_en = rating_type_badge("al")
    assert "BUY" in badge_en

    set_language("tr")
    badge_tr = rating_type_badge("al")
    assert "AL" in badge_tr

    # Reset
    set_language("en")


def test_formatter_notification_status_localized(capsys):
    from datetime import datetime
    status = NotificationUnreadStatus(
        has_unread=True,
        read_at=datetime.fromisoformat("2026-09-22T15:05:06Z"),
    )

    set_language("en")
    print_notification_status(status)

    set_language("tr")
    print_notification_status(status)

    # Reset
    set_language("en")


def test_cli_help_lang_en():
    set_language("en")
    result = runner.invoke(app, ["--lang", "en", "--help"])
    assert result.exit_code == 0
    assert "Fintables Mobile API Client and CLI Tool" in result.output
    assert "company" in result.output


def test_cli_help_lang_tr():
    set_language("tr")
    result = runner.invoke(app, ["--lang", "tr", "--help"])
    assert result.exit_code == 0
    assert "Fintables Mobil API İstemcisi ve CLI Aracı" in result.output
    assert "company" in result.output


def test_sync_cli_translations_no_double_iteration():
    """sync_cli_translations(lang) must iterate _CLI_REGISTRY exactly once,
    not twice due to a circular call with set_language."""
    set_language("en")
    registry_size = len(_CLI_REGISTRY)
    if registry_size == 0:
        pytest.skip("No CLI targets registered")

    call_count = 0
    original_t = t

    def counting_t(key, **kwargs):
        nonlocal call_count
        call_count += 1
        return original_t(key, **kwargs)

    with patch("fintables.i18n.t", side_effect=counting_t):
        sync_cli_translations("tr")

    assert get_language() == "tr"
    # t() should be called exactly once per registry entry, not twice
    assert call_count == registry_size, (
        f"Expected {registry_size} calls to t(), got {call_count}. "
        f"Circular call between sync_cli_translations and set_language?"
    )


def test_set_language_triggers_sync():
    """set_language() called directly (e.g. from CLI callback) must still
    trigger sync_cli_translations to update registered targets."""
    set_language("en")

    # Create a mock target and register it
    class MockTarget:
        help = "original"
    mock = MockTarget()

    _CLI_REGISTRY.append((mock, "cli.app.help"))
    try:
        set_language("tr")
        assert get_language() == "tr"
        # The mock target's help should be updated to Turkish
        assert mock.help == t("cli.app.help")
        assert "Fintables" in mock.help
    finally:
        _CLI_REGISTRY.remove((mock, "cli.app.help"))
        set_language("en")


def test_sync_cli_translations_sets_language_and_updates_targets():
    """sync_cli_translations(lang) must both set the language and update targets."""
    set_language("en")

    class MockTarget:
        help = "original"
    mock = MockTarget()

    _CLI_REGISTRY.append((mock, "cli.app.help"))
    try:
        sync_cli_translations("tr")
        assert get_language() == "tr"
        expected = t("cli.app.help")
        assert mock.help == expected
        assert "Fintables" in mock.help
    finally:
        _CLI_REGISTRY.remove((mock, "cli.app.help"))
        set_language("en")
