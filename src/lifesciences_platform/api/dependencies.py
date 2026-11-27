"""Things routes receive from FastAPI. Tests replace them with `dependency_overrides`."""

from collections.abc import Iterator
from datetime import UTC, date, datetime
from functools import lru_cache

from sqlalchemy.orm import Session, sessionmaker

from lifesciences_platform.common.config import get_settings
from lifesciences_platform.common.db import create_db_engine, create_session_factory


@lru_cache
def _session_factory() -> sessionmaker[Session]:
    # Built on first use, so the app starts (and /health answers) without a database.
    return create_session_factory(create_db_engine(get_settings()))


def get_validation_date() -> date:
    """The day a collection date may not be later than. UTC, so servers agree."""
    return datetime.now(UTC).date()


def get_session() -> Iterator[Session]:
    """One session per request, closed afterwards. Uncommitted work is discarded."""
    with _session_factory()() as session:
        yield session
