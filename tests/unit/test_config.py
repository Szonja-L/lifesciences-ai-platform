"""Settings load from the environment, defaults work, bad values are rejected."""

from pathlib import Path

import pytest
from pydantic import ValidationError

from lifesciences_platform.common.config import Settings

SETTING_VARS = [
    "APP_ENV",
    "LOG_LEVEL",
    "DATABASE_URL",
    "ANTHROPIC_API_KEY",
    "LLM_MONTHLY_BUDGET_EUR",
    "MAX_UPLOAD_BYTES",
    "UPLOAD_DIR",
    "MAX_MANIFEST_ROWS",
]


@pytest.fixture(autouse=True)
def clean_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Start every test with none of the setting variables defined."""
    for name in SETTING_VARS:
        monkeypatch.delenv(name, raising=False)


def make_settings() -> Settings:
    # _env_file=None: a developer's local .env must not change test results.
    return Settings(_env_file=None)


def test_defaults() -> None:
    settings = make_settings()
    assert settings.app_env == "dev"
    assert settings.log_level == "INFO"
    assert settings.database_url is None
    assert settings.anthropic_api_key is None
    assert settings.llm_monthly_budget_eur is None
    assert settings.max_upload_bytes == 5 * 1024 * 1024
    assert settings.upload_dir == Path.home() / ".lifesciences-platform" / "uploads"
    assert settings.max_manifest_rows == 1000


def test_upload_dir_expands_home(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("UPLOAD_DIR", "~/manifests")
    assert make_settings().upload_dir == Path.home() / "manifests"


def test_values_come_from_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("LLM_MONTHLY_BUDGET_EUR", "12.5")
    settings = make_settings()
    assert settings.app_env == "test"
    assert settings.log_level == "DEBUG"
    assert settings.llm_monthly_budget_eur == 12.5


def test_empty_values_count_as_unset(monkeypatch: pytest.MonkeyPatch) -> None:
    # This is what a freshly copied .env.example contains.
    monkeypatch.setenv("DATABASE_URL", "")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "")
    monkeypatch.setenv("LLM_MONTHLY_BUDGET_EUR", "")
    settings = make_settings()
    assert settings.database_url is None
    assert settings.anthropic_api_key is None
    assert settings.llm_monthly_budget_eur is None


def test_secrets_are_not_printed(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ANTHROPIC_API_KEY", "not-a-real-key")
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:not-a-real-password@localhost/db")
    settings = make_settings()
    assert settings.anthropic_api_key is not None
    assert settings.anthropic_api_key.get_secret_value() == "not-a-real-key"
    text = repr(settings)
    assert "not-a-real-key" not in text
    assert "not-a-real-password" not in text


@pytest.mark.parametrize(
    ("name", "value"),
    [
        ("APP_ENV", "staging"),
        ("LOG_LEVEL", "LOUD"),
        ("LLM_MONTHLY_BUDGET_EUR", "-1"),
        ("LLM_MONTHLY_BUDGET_EUR", "abc"),
        ("MAX_UPLOAD_BYTES", "0"),
        ("MAX_MANIFEST_ROWS", "0"),
        ("UPLOAD_DIR", "uploads"),
    ],
)
def test_invalid_values_are_rejected(
    monkeypatch: pytest.MonkeyPatch, name: str, value: str
) -> None:
    monkeypatch.setenv(name, value)
    with pytest.raises(ValidationError):
        make_settings()
