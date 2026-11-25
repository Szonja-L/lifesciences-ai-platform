"""Application settings, loaded from environment variables (and an optional local .env file).

Secrets are never hard-coded. Missing optional values are `None`, never silently
replaced by a made-up default (CLAUDE.md rules 8 and 10).
"""

from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

AppEnv = Literal["dev", "test", "prod"]
LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


class Settings(BaseSettings):
    """Typed settings. Environment variable names match the field names (case-insensitive)."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        # `.env.example` ships empty values; treat "" as "not set" instead of a parse error.
        env_ignore_empty=True,
    )

    app_env: AppEnv = "dev"
    log_level: LogLevel = "INFO"

    # Placeholders: nothing uses these until the tasks that need them.
    database_url: SecretStr | None = None  # may contain a password, so SecretStr
    anthropic_api_key: SecretStr | None = None
    # None means "not configured". What the LLMClient does then is decided in its own task.
    llm_monthly_budget_eur: float | None = Field(default=None, ge=0)


@lru_cache
def get_settings() -> Settings:
    """Return the process-wide settings, read once. Tests build `Settings(...)` directly."""
    return Settings()
