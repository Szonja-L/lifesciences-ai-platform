"""Alembic environment: connects with the project settings and compares against `Base.metadata`.

The database URL comes from `Settings` (DATABASE_URL in .env or the environment), never
from alembic.ini, so the password stays out of version control.
"""

from logging.config import fileConfig

from alembic import context
from sqlalchemy import Connection

import lifesciences_platform.workflows.models  # noqa: F401  (registers the tables on Base)
from lifesciences_platform.common.config import get_settings
from lifesciences_platform.common.db import Base, create_db_engine, database_url_from

config = context.config

if config.config_file_name is not None:
    # Keep loggers created before this point (the app's, pytest's) working.
    fileConfig(config.config_file_name, disable_existing_loggers=False)

target_metadata = Base.metadata
# Also detect column type changes in autogenerate and `alembic check`.
COMPARE_TYPE = True


def run_migrations_offline() -> None:
    """Emit SQL to stdout instead of running it (`alembic upgrade head --sql`)."""
    context.configure(
        url=database_url_from(get_settings()),
        target_metadata=target_metadata,
        compare_type=COMPARE_TYPE,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def _run_with_connection(connection: Connection) -> None:
    context.configure(
        connection=connection, target_metadata=target_metadata, compare_type=COMPARE_TYPE
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations against the live database.

    A caller (a test, for example) may pass its own connection in
    `config.attributes["connection"]`; otherwise an engine is built from the settings.
    """
    connection = config.attributes.get("connection")
    if connection is not None:
        _run_with_connection(connection)
        return
    engine = create_db_engine(get_settings())
    try:
        with engine.connect() as new_connection:
            _run_with_connection(new_connection)
    finally:
        engine.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
