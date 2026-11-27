# Life Sciences AI and Workflow Automation Platform

[![CI](https://github.com/Szonja-L/lifesciences-ai-platform/actions/workflows/ci.yml/badge.svg)](https://github.com/Szonja-L/lifesciences-ai-platform/actions/workflows/ci.yml)

Portfolio programme, started November 2026. One platform, three tracks:

- **Track A.** Genomics service-provider workflow: submission intake, validation, QC, pipeline execution, draft report, human approval, audit trail.
- **Track B.** Scientific document intelligence: typed extraction from PDFs with page-level provenance, entity extraction, search, question answering with citations, measured against a hand-labelled set.
- **Track C.** One professional-grade variant QC and annotation pipeline in Snakemake, run in CI, with provenance and a reference comparison.

Developed in discussion with Clementine, who mentors and reviews the document-intelligence work. All data is public or synthetic and labelled as such. Nothing here is clinical decision support.

The full plan and roadmap are in [PROJECT_PLAN.md](PROJECT_PLAN.md). The running state is in [PROGRESS.md](PROGRESS.md). Paste-ready session and task prompts are in [prompts/](prompts/README.md). Decisions are recorded in `docs/decisions/`. Monthly evidence packages live in `docs/evidence/`.

## Status

Plan written and committed 2026-11-13. Prompt kit and Python skeleton in place; FastAPI app with `/health` and typed settings added in task 0.2. PostgreSQL, the submission data model and the first migration added in task 1.1. Next: see PROGRESS.md.

## Running locally

Requirements: Python 3.12 and GNU Make. On Windows, Make was installed with `winget install ezwinports.make --source winget` (open a new terminal afterwards so `make` is on the PATH).

Windows (PowerShell), as run on 2026-11-25:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
make install   # editable install plus ruff, mypy, pytest
make check     # lint, type-check, tests
```

Linux or macOS:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
make install
make check
```

## Database

PostgreSQL 16 runs in Docker (Docker Desktop on Windows). Copy the settings template once and choose your own local password in `.env` (change it in both `POSTGRES_PASSWORD` and `DATABASE_URL`):

```powershell
Copy-Item .env.example .env       # then edit the password in .env
docker compose up -d              # start Postgres (data kept in the `pgdata` volume)
python -m alembic upgrade head    # create or update the tables
python -m alembic current         # shows "0001 (head)" when up to date
```

`DATABASE_URL` must start with `postgresql+psycopg://` and use `127.0.0.1`, not `localhost`: on Windows `localhost` tries IPv6 first, and the container listens on IPv4 only. Stop the database with `docker compose down`; `docker compose down -v` also deletes its data.

The database tests (`pytest -m db`) run inside a rolled-back transaction, so they never change your data. If Postgres is not running they are skipped with a message; set `REQUIRE_DB=1` to make that a failure instead (CI does). After changing a model, create a migration with `python -m alembic revision --autogenerate -m "what changed"`, read it, then apply it. Design choices are in [docs/decisions/0004-database-and-status-column.md](docs/decisions/0004-database-and-status-column.md).

## Starting the API

Copy the settings template once (see Database above), then start the server from the activated virtual environment:

```powershell
Copy-Item .env.example .env
python -m uvicorn lifesciences_platform.api.main:app --reload
```

Open <http://127.0.0.1:8000/health>; it returns `{"status":"ok","version":"0.0.1"}`. Interactive docs are at <http://127.0.0.1:8000/docs>. If port 8000 is taken, add `--port 8011` (or any free port). Settings are described in `.env.example`; `.env` is git-ignored and must never be committed.

CI (GitHub Actions, `.github/workflows/ci.yml`) runs `make check` on Ubuntu with Python 3.12 for every push to `main` and every pull request: ruff lint and format check, strict mypy and pytest. A PostgreSQL 16 service container is started first and `alembic upgrade head` is applied, so the database tests run in CI too.

Individual targets: `make lint`, `make typecheck`, `make test`. Tool choices are explained in [docs/decisions/0002-python-tooling.md](docs/decisions/0002-python-tooling.md).
