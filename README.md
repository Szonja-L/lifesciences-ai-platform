# Life Sciences AI and Workflow Automation Platform

[![CI](https://github.com/Szonja-L/lifesciences-ai-platform/actions/workflows/ci.yml/badge.svg)](https://github.com/Szonja-L/lifesciences-ai-platform/actions/workflows/ci.yml)

Portfolio programme, started November 2026. One platform, three tracks:

- **Track A.** Genomics service-provider workflow: submission intake, validation, QC, pipeline execution, draft report, human approval, audit trail.
- **Track B.** Scientific document intelligence: typed extraction from PDFs with page-level provenance, entity extraction, search, question answering with citations, measured against a hand-labelled set.
- **Track C.** One professional-grade variant QC and annotation pipeline in Snakemake, run in CI, with provenance and a reference comparison.

Developed in discussion with Clementine, who mentors and reviews the document-intelligence work. All data is public or synthetic and labelled as such. Nothing here is clinical decision support.

The full plan and roadmap are in [PROJECT_PLAN.md](PROJECT_PLAN.md). The running state is in [PROGRESS.md](PROGRESS.md). Paste-ready session and task prompts are in [prompts/](prompts/README.md). Decisions are recorded in `docs/decisions/`. Monthly evidence packages live in `docs/evidence/`.

## Status

Plan written and committed 2026-11-13. Prompt kit and Python skeleton in place; FastAPI app with `/health` and typed settings added in task 0.2. PostgreSQL, the submission data model and the first migration added in task 1.1. File upload (`POST /submissions`) added in task 1.2. Manifest validation engine added in task 1.3. Validation on upload, stored results and the two read endpoints added in task 1.4. Next: see PROGRESS.md.

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

## Uploading a manifest

`POST /submissions` takes one `.csv` file and four form fields. With the database up and the API running, in PowerShell (use `curl.exe`; plain `curl` is a PowerShell alias for a different command):

```powershell
curl.exe -X POST http://127.0.0.1:8000/submissions `
  -F "file=@tests/fixtures/manifests/valid.csv;type=text/csv" `
  -F "client_id=C-001" `
  -F "project_name=Synthetic exome batch A" `
  -F "requested_analysis=variant_annotation" `
  -F "contact_email=lab-contact@example.org"
```

On Linux or macOS use `curl` and `\` line endings. Keep `;type=text/csv`: curl does not recognise `.csv` and would send a type the API rejects.

The file is validated as part of the upload. A 201 response means it was accepted and recorded, not that it is valid; read `status`:

| `status` | Meaning |
|---|---|
| `VALIDATED` | No errors (there may be warnings) |
| `VALIDATION_FAILED` | At least one error; read the issues |
| `SUBMITTED` | Validation could not be completed; the reason is in the server log |

The response also holds the submission id, filename, SHA-256 hash, size, time and rule set version. The rules are in `src/lifesciences_platform/common/validation/`.

| Response | Meaning |
|---|---|
| 409 `DUPLICATE_FILE` | These exact bytes were already submitted; the response names that submission |
| 413 `FILE_TOO_LARGE` | Over `MAX_UPLOAD_BYTES` (default 5 MB) |
| 415 `UNSUPPORTED_FILE_TYPE` | Not a `.csv` file, or not sent as `text/csv` or `application/vnd.ms-excel` |
| 422 | A file or form field is missing or invalid |
| 503 | The database or the upload folder is unavailable |

Files are stored as `<hash>.csv` in `UPLOAD_DIR`, by default `~/.lifesciences-platform/uploads`. Why: [docs/decisions/0005-upload-storage.md](docs/decisions/0005-upload-storage.md).

## Reading results

```powershell
curl.exe "http://127.0.0.1:8000/submissions?limit=20&offset=0"
curl.exe http://127.0.0.1:8000/submissions/<id>
```

The list is newest first, with `limit` from 1 to 100 (default 20), and returns `items`, `total`, `limit` and `offset`. One submission by id adds its metadata and every issue (`severity`, `code`, `message`, `row`, `column`, `rule_set_version`); an unknown id gives 404. All three endpoints are described at <http://127.0.0.1:8000/docs>. Design: [docs/decisions/0007-validation-on-upload-and-read-api.md](docs/decisions/0007-validation-on-upload-and-read-api.md).

## Checks and CI

CI (GitHub Actions, `.github/workflows/ci.yml`) runs `make check` on Ubuntu with Python 3.12 for every push to `main` and every pull request: ruff lint and format check, strict mypy and pytest. A PostgreSQL 16 service container is started first and `alembic upgrade head` is applied, so the database tests run in CI too.

Individual targets: `make lint`, `make typecheck`, `make test`. Tool choices are explained in [docs/decisions/0002-python-tooling.md](docs/decisions/0002-python-tooling.md).
