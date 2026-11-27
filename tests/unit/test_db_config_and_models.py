"""Database module and model metadata checks that need no running database."""

import pytest
from pydantic import SecretStr
from sqlalchemy import CheckConstraint, UniqueConstraint

from lifesciences_platform.common.config import Settings
from lifesciences_platform.common.db import Base, DatabaseNotConfiguredError, database_url_from
from lifesciences_platform.workflows.models import (
    Submission,
    SubmissionStatus,
    ValidationResult,
)


def settings_with_url(url: str | None) -> Settings:
    return Settings(_env_file=None, database_url=SecretStr(url) if url is not None else None)


def test_missing_database_url_raises_clear_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)
    with pytest.raises(DatabaseNotConfiguredError, match="DATABASE_URL is not set"):
        database_url_from(settings_with_url(None))


def test_url_without_psycopg_driver_is_rejected_without_echoing_it() -> None:
    url = "postgresql://user:secret-pw@127.0.0.1:5432/db"
    with pytest.raises(DatabaseNotConfiguredError) as error:
        database_url_from(settings_with_url(url))
    assert "postgresql+psycopg://" in str(error.value)
    assert "secret-pw" not in str(error.value)


def test_psycopg_url_is_returned() -> None:
    url = "postgresql+psycopg://user:pw@127.0.0.1:5432/db"
    assert database_url_from(settings_with_url(url)) == url


def test_both_tables_are_registered() -> None:
    assert {"submissions", "validation_results"} <= set(Base.metadata.tables)


def constraint_names(table_name: str, kind: type) -> set[str]:
    table = Base.metadata.tables[table_name]
    return {str(c.name) for c in table.constraints if isinstance(c, kind)}


def test_submission_constraints_have_stable_names() -> None:
    checks = constraint_names("submissions", CheckConstraint)
    assert {"ck_submissions_status_allowed", "ck_submissions_size_bytes_non_negative"} <= checks
    uniques = {
        tuple(c.columns.keys())
        for c in Base.metadata.tables["submissions"].constraints
        if isinstance(c, UniqueConstraint)
    }
    assert ("content_hash",) in uniques


def test_status_check_allows_exactly_the_phase_1_states() -> None:
    assert [s.value for s in SubmissionStatus] == ["SUBMITTED", "VALIDATED", "VALIDATION_FAILED"]
    status_check = next(
        c
        for c in Base.metadata.tables["submissions"].constraints
        if isinstance(c, CheckConstraint) and c.name == "ck_submissions_status_allowed"
    )
    sql = str(status_check.sqltext)
    for status in SubmissionStatus:
        assert f"'{status.value}'" in sql


def test_reserved_names_are_avoided() -> None:
    # "metadata" is reserved on the declarative Base; "column" is reserved in Postgres.
    assert "metadata" in Submission.__table__.columns
    assert "column_name" in ValidationResult.__table__.columns
    assert "row_number" in ValidationResult.__table__.columns
