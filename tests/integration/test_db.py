"""Tests against the real PostgreSQL database from docker-compose.yml.

Each test runs inside a transaction that is rolled back, so local data is never changed.
When the database is not reachable the tests are skipped with instructions, unless
REQUIRE_DB=1 (set in CI), which turns the skip into a failure.
"""

import hashlib
import os
import uuid
from collections.abc import Iterator
from pathlib import Path
from typing import NoReturn

import pytest
from alembic import command
from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy import Engine, select, text
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.orm import Session

from lifesciences_platform.common.config import Settings
from lifesciences_platform.common.db import DatabaseNotConfiguredError, create_db_engine
from lifesciences_platform.workflows.models import (
    Severity,
    Submission,
    SubmissionStatus,
    ValidationResult,
)

pytestmark = pytest.mark.db

REPO_ROOT = Path(__file__).resolve().parents[2]
HOW_TO_START = (
    "Start it with `docker compose up -d` and `alembic upgrade head` (README, 'Database')."
)


def _unavailable(reason: str) -> NoReturn:
    if os.environ.get("REQUIRE_DB") == "1":
        pytest.fail(f"REQUIRE_DB=1 but {reason}")
    pytest.skip(f"{reason}. {HOW_TO_START}")


@pytest.fixture(scope="module")
def engine() -> Iterator[Engine]:
    try:
        db_engine = create_db_engine(Settings())
    except DatabaseNotConfiguredError as error:
        _unavailable(str(error))
    try:
        with db_engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except OperationalError:
        db_engine.dispose()
        _unavailable("PostgreSQL is not reachable at DATABASE_URL")
    yield db_engine
    db_engine.dispose()


@pytest.fixture
def session(engine: Engine) -> Iterator[Session]:
    """A session whose work, including commits, is rolled back at the end of the test."""
    with engine.connect() as connection:
        transaction = connection.begin()
        db_session = Session(bind=connection, join_transaction_mode="create_savepoint")
        try:
            yield db_session
        finally:
            db_session.close()
            transaction.rollback()


def make_submission(content: bytes = b"sample_id\nS-0001\n") -> Submission:
    return Submission(
        filename="valid.csv",
        content_hash=hashlib.sha256(content).hexdigest(),
        size_bytes=len(content),
        submission_metadata={
            "client_id": "C-001",
            "project_name": "Synthetic exome batch A",
            "requested_analysis": "variant_annotation",
            "contact_email": "lab-contact@example.org",
        },
    )


def test_database_is_migrated_to_head(engine: Engine) -> None:
    config = Config(str(REPO_ROOT / "alembic.ini"))
    head = ScriptDirectory.from_config(config).get_current_head()
    with engine.connect() as connection:
        current = MigrationContext.configure(connection).get_current_revision()
    assert current == head, (
        f"Database at {current!r}, code at {head!r}. Run `alembic upgrade head`."
    )


def test_models_and_migrations_agree(engine: Engine) -> None:
    """`alembic check` fails if the models changed without a matching migration."""
    config = Config(str(REPO_ROOT / "alembic.ini"))
    with engine.connect() as connection:
        config.attributes["connection"] = connection
        command.check(config)


def test_create_and_read_submission_with_result(session: Session) -> None:
    submission = make_submission()
    submission.validation_results.append(
        ValidationResult(
            rule_set_version="v1",
            severity=Severity.ERROR.value,
            code="MISSING_VALUE",
            message="sample_id is empty; expected S- followed by 4 digits.",
            row_number=3,
            column_name="sample_id",
        )
    )
    session.add(submission)
    session.commit()
    submission_id = submission.id  # read before detaching; commit expired the attributes
    session.expunge_all()  # force the read below to come from the database

    stored = session.scalars(select(Submission).where(Submission.id == submission_id)).one()
    assert isinstance(stored.id, uuid.UUID)
    assert stored.status == SubmissionStatus.SUBMITTED
    assert stored.rule_set_version is None
    assert stored.created_at.tzinfo is not None
    assert stored.submission_metadata["client_id"] == "C-001"
    [result] = stored.validation_results
    assert (result.code, result.row_number, result.column_name) == ("MISSING_VALUE", 3, "sample_id")


def test_duplicate_content_hash_is_rejected(session: Session) -> None:
    session.add(make_submission())
    session.commit()
    session.add(make_submission())
    with pytest.raises(IntegrityError, match="uq_submissions_content_hash"):
        session.flush()


def test_unknown_status_is_rejected(session: Session) -> None:
    submission = make_submission()
    submission.status = "RUNNING"  # a later-phase state, not allowed yet
    session.add(submission)
    with pytest.raises(IntegrityError, match="ck_submissions_status_allowed"):
        session.flush()


def test_header_row_number_is_rejected(session: Session) -> None:
    submission = make_submission()
    submission.validation_results.append(
        ValidationResult(
            rule_set_version="v1",
            severity=Severity.ERROR.value,
            code="MISSING_VALUE",
            message="line 1 is the header",
            row_number=1,
        )
    )
    session.add(submission)
    with pytest.raises(IntegrityError, match="ck_validation_results_row_number_data_line"):
        session.flush()


def test_deleting_a_submission_deletes_its_results(session: Session) -> None:
    submission = make_submission()
    submission.validation_results.append(
        ValidationResult(
            rule_set_version="v1",
            severity=Severity.WARNING.value,
            code="UNKNOWN_COLUMN",
            message="Column 'notes' is not in rule set v1.",
            column_name="notes",
        )
    )
    session.add(submission)
    session.flush()
    session.execute(text("DELETE FROM submissions WHERE id = :id"), {"id": submission.id})
    remaining = session.scalar(
        select(ValidationResult.id).where(ValidationResult.submission_id == submission.id)
    )
    assert remaining is None
