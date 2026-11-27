"""Application settings, loaded from environment variables (and an optional local .env file).

Secrets are never hard-coded. Missing optional values are `None`, never silently
replaced by a made-up default (CLAUDE.md rules 8 and 10).
"""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

AppEnv = Literal["dev", "test", "prod"]
LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

DEFAULT_MAX_UPLOAD_BYTES = 5 * 1024 * 1024  # track-a-spec.md section 7


def default_upload_dir() -> Path:
    """In the user's home folder, so uploads never land inside the repository."""
    return Path.home() / ".lifesciences-platform" / "uploads"


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

    max_upload_bytes: int = Field(default=DEFAULT_MAX_UPLOAD_BYTES, gt=0)
    upload_dir: Path = Field(default_factory=default_upload_dir)

    @field_validator("upload_dir")
    @classmethod
    def _upload_dir_must_be_absolute(cls, value: Path) -> Path:
        # A relative path would resolve against wherever the server was started,
        # which during development is the repository.
        expanded = value.expanduser()
        if not expanded.is_absolute():
            raise ValueError("UPLOAD_DIR must be an absolute path (or start with ~)")
        return expanded


@lru_cache
def get_settings() -> Settings:
    """Return the process-wide settings, read once. Tests build `Settings(...)` directly."""
    return Settings()
