"""Database access: the declarative base, the engine and the session factory.

All tables in the project share one `Base` (and so one `MetaData` and one Alembic
history). Models live next to the feature that owns them, for example
`lifesciences_platform.workflows.models`.

The connection string comes from `Settings.database_url`; it is never read from
`alembic.ini` or hard-coded (CLAUDE.md rule 8).
"""

from sqlalchemy import Engine, MetaData, create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from lifesciences_platform.common.config import Settings

# Deterministic constraint names. Without them Postgres invents names, and a later
# migration that widens a check constraint (for example the submission status) could
# not refer to it reliably. See ADR 0004.
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

REQUIRED_DRIVER_PREFIX = "postgresql+psycopg://"


class Base(DeclarativeBase):
    """Base class for every ORM model in the project."""

    metadata = MetaData(naming_convention=NAMING_CONVENTION)


class DatabaseNotConfiguredError(RuntimeError):
    """DATABASE_URL is missing or does not name the psycopg 3 driver."""


def database_url_from(settings: Settings) -> str:
    """Return the connection string, or raise a message that says how to fix it."""
    if settings.database_url is None:
        raise DatabaseNotConfiguredError(
            "DATABASE_URL is not set. Copy .env.example to .env, then run "
            "`docker compose up -d` (see README, 'Database')."
        )
    url = settings.database_url.get_secret_value()
    if not url.startswith(REQUIRED_DRIVER_PREFIX):
        # Plain postgresql:// would make SQLAlchemy look for psycopg2, which is not installed.
        # The URL itself is not echoed: it may contain a password.
        raise DatabaseNotConfiguredError(
            f"DATABASE_URL must start with {REQUIRED_DRIVER_PREFIX!r} (psycopg 3 driver)."
        )
    return url


# Seconds to wait for a connection. Without a limit, a stopped database can leave a
# request (or the test suite) hanging for minutes instead of failing with a clear error.
CONNECT_TIMEOUT_SECONDS = 5


def create_db_engine(settings: Settings) -> Engine:
    """Build an engine. `pool_pre_ping` replaces connections the server has closed."""
    return create_engine(
        database_url_from(settings),
        pool_pre_ping=True,
        connect_args={"connect_timeout": CONNECT_TIMEOUT_SECONDS},
    )


def create_session_factory(engine: Engine) -> sessionmaker[Session]:
    """Sessions that keep loaded attributes after commit, so API code can read them."""
    return sessionmaker(bind=engine, expire_on_commit=False)
