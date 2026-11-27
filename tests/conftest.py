"""Shared fixtures for tests against the real PostgreSQL database.

Each test runs inside a transaction that is rolled back, so local data is never changed.
When the database is not reachable the tests are skipped with instructions, unless
REQUIRE_DB=1 (set in CI), which turns the skip into a failure.
"""

import os
from collections.abc import Iterator
from typing import NoReturn

import pytest
from sqlalchemy import Connection, Engine, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from lifesciences_platform.common.config import Settings
from lifesciences_platform.common.db import DatabaseNotConfiguredError, create_db_engine

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
def db_connection(engine: Engine) -> Iterator[Connection]:
    """A connection whose outer transaction is rolled back at the end of the test."""
    with engine.connect() as connection:
        transaction = connection.begin()
        try:
            yield connection
        finally:
            transaction.rollback()


@pytest.fixture
def session(db_connection: Connection) -> Iterator[Session]:
    """A session whose work, including commits, is rolled back with the connection."""
    db_session = Session(bind=db_connection, join_transaction_mode="create_savepoint")
    try:
        yield db_session
    finally:
        db_session.close()
