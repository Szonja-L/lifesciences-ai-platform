# ADR 0004: Database, migrations and the submission status column

- Status: accepted
- Date: 2026-11-25
- Task: 1.1

## Context

Track A needs to store submissions and their validation issues (spec: `docs/architecture/track-a-spec.md`). Later phases add QC, pipeline runs, reports and an audit trail on top of the same tables, so the first schema and the way it changes over time will be used for the whole programme.

## Decisions

**PostgreSQL 16 in Docker Compose for development.** One `docker compose up -d` gives every machine the same database. The port is bound to `127.0.0.1` only. Credentials come from `.env`; Compose refuses to start if one is missing instead of using a default password.

**SQLAlchemy 2 with typed `Mapped[]` models, psycopg 3 as the driver.** Typed models are checked by strict mypy like the rest of the code. psycopg 3 installs from binary wheels on Windows and is the maintained successor of psycopg2. `DATABASE_URL` must start with `postgresql+psycopg://`; `db.py` refuses other prefixes with a message, without echoing the URL (it may contain a password). Connections time out after 5 seconds, so a stopped database fails fast.

**Alembic for migrations, URL from settings.** `migrations/env.py` reads `DATABASE_URL` through `Settings`, never from `alembic.ini`, so no password is written into version control. Migrations are generated with `--autogenerate`, then read and cleaned by hand; ruff runs on every new revision through a post-write hook. `migrations/` is type-checked by mypy. A test runs `alembic check`, which fails if the models change without a matching migration.

**One shared `Base` with a constraint naming convention.** Every constraint gets a predictable name (`ck_submissions_status_allowed`, `uq_submissions_content_hash`). A later migration can then drop and recreate a constraint by name instead of guessing a name Postgres invented.

**Status column: `VARCHAR(32)` plus a named check constraint, not a native Postgres `ENUM`.** The allowed values come from the `SubmissionStatus` StrEnum and are, for Phase 1, only `SUBMITTED`, `VALIDATED`, `VALIDATION_FAILED`. Each later phase adds its states with a small migration that recreates `ck_submissions_status_allowed`. A native enum needs `ALTER TYPE ... ADD VALUE` for each new state, a value cannot be removed again without rebuilding the type, and Alembic autogenerate does not detect enum value changes. A check constraint is plain SQL, reversible, and still makes the database reject any state the code does not handle yet. Transitions between states (the state machine) are application logic and belong to a later phase.

**Identifiers.** Submissions use a UUID generated in Python: the id appears in URLs and reports, and a sequential number would reveal volumes and invite guessing. Validation results use a `BIGINT` identity: they are never addressed on their own, and insertion order is their natural order.

**Integrity rules live in the database too.** `content_hash` (SHA-256, `CHAR(64)`) is unique, so two identical uploads cannot both be stored even if they arrive at the same moment; the API maps the violation to HTTP 409 (task 1.2). `size_bytes >= 0`; severity is `error` or `warning`; a result's row number is null (file or header level) or at least 2, because line 1 is the header. Deleting a submission deletes its results (`ON DELETE CASCADE`).

**Two columns beyond the task list.** `rule_set_version` on `Submission` (null until validated): a file that passes with zero issues has no result rows, so without it the system could not say which rules the file passed, which the spec requires. `updated_at`: the spec stores status and timestamps in Phase 1.

**Naming clashes avoided.** `metadata` is reserved on SQLAlchemy's declarative base, so the Python attribute is `submission_metadata` mapped to a column named `metadata` (JSONB). `column` is a reserved word in PostgreSQL, so the result columns are `row_number` and `column_name`; the API and reports can still label them "row" and "column".

**Tests.** Database tests are marked `db` and run inside a transaction that is rolled back, so they never change local data. When the database is unreachable they are skipped with the commands to start it. CI runs a PostgreSQL 16 service container, applies the migrations, and sets `REQUIRE_DB=1`, which turns a skip into a failure; a broken service container therefore cannot produce a green run that tested nothing.

## Dependencies added

`sqlalchemy` (ORM), `alembic` (migrations), `psycopg[binary]` (driver).

## Trade-offs

- The Postgres user and password appear twice in `.env`: once for Compose (`POSTGRES_*`) and once inside `DATABASE_URL`. Building the URL from parts would remove that, at the cost of more settings code.
- Rolled-back transactions are lighter than a separate test database, but tests share the developer's schema, so they need `alembic upgrade head` to have run (a test checks this and says so).
- The image is pinned to major version 16, not a minor version, so a `docker compose pull` can bring patch updates.

## Not decided here

The state machine and its transitions, the audit trail table, request-scoped sessions in FastAPI (task 1.2 or 1.4), connection pool sizing, and production database hosting.
