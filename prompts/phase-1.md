# Phase 1: submission-intake MVP (plan weeks 3-4)

Reference: PROJECT_PLAN.md section 12.3, section 9 Month 1 weeks 3-4, section 8.2 (reusable components), `docs/architecture/track-a-spec.md`.
Phase gate: upload a manifest, see errors or stored records, download a report; tests on all five fixtures; CI green; evidence package 1; tag `v0.1`.
Out of scope for the whole phase: the Claude API, Snakemake, state machine beyond "submitted" and "validated / validation failed", authentication.

Paste one task block per session, after `prompts/session-start.md`.

---

## Task 1.1 PostgreSQL, data models, first migration

Model: Opus (data model decisions persist for the whole programme).

Goal: a database that starts with one command and holds submissions and validation results.

Reads: track-a-spec.md (manifest schema, metadata), PROJECT_PLAN.md section 8.2; config.py.

Produces:
- `docker-compose.yml` with a Postgres 16 service, named volume, healthcheck, credentials from `.env`.
- SQLAlchemy 2 (typed, `Mapped[]`) models in `src/lifesciences_platform/workflows/models.py`: `Submission` (id, created_at, filename, content_hash, size_bytes, status, metadata JSON) and `ValidationResult` (id, submission_id, rule_set_version, severity, code, message, row, column, created_at).
- Alembic set up under `migrations/`, first migration generated and applied.
- `common/db.py` with engine and session factory from settings.
- Tests: a DB test that creates and reads a submission against the compose database, skipped with a clear message when the database is not reachable. ADR 0003 on SQLAlchemy + Alembic and the status column design.
- README: `docker compose up -d`, `alembic upgrade head`.

Acceptance: compose up, migration applied, `make check` green including the DB test locally. CI stays green (DB test skipped or run with a service container; say which and why).

Do not: add the full state machine, workers or any pipeline table.

---

## Task 1.2 File upload endpoint

Model: Sonnet.

Goal: a safe upload path that creates a submission row.

Reads: models.py, config.py, track-a-spec.md (allowed file types, size limit).

Produces:
- `POST /submissions` accepting a multipart file plus metadata fields: rejects unsupported extensions and content types, enforces a size limit from settings, computes a SHA-256 content hash, stores the file under `uploads/<hash>.<ext>` outside the package, creates the `Submission` row with status `submitted`.
- Pydantic response model.
- Tests: valid upload creates row and file; oversize, wrong type, empty body and duplicate hash each return the right 4xx with a clear message.

Acceptance: tests green, curl example in README.

Do not: validate the CSV contents yet. Do not store files inside the repository tree.

---

## Task 1.3 Validation engine

Model: Sonnet.

Goal: a pure, tested module that turns a manifest file into typed validation results against a versioned rule set.

Reads: track-a-spec.md manifest schema; the five fixtures.

Produces:
- `src/lifesciences_platform/common/validation/`: `rules.py` (rule set `v1` as data: required columns, column types, allowed values, uniqueness of sample id), `engine.py` (`validate_manifest(path, rule_set) -> list[ValidationIssue]`), `models.py` (Pydantic `ValidationIssue` with severity, code, message, row, column).
- Error codes are stable strings (for example `MISSING_COLUMN`, `INVALID_VALUE`, `EMPTY_FILE`, `DUPLICATE_SAMPLE_ID`).
- Unit tests: every fixture produces the expected codes; a valid file produces none; malformed CSV does not crash.

Acceptance: tests green; the rule set is readable without reading the engine.

Do not: touch the database or API in this task.

---

## Task 1.4 Persist results and read endpoints

Model: Sonnet.

Goal: validation runs on upload, results are stored, and the API exposes them.

Reads: tasks 1.1 to 1.3 outputs.

Produces:
- Upload now runs validation after storing the file; submission status becomes `validated` or `validation_failed`; issues stored as `ValidationResult` rows with `rule_set_version`.
- `GET /submissions` (paginated list) and `GET /submissions/{id}` (submission plus issues).
- Integration tests on the valid and the missing-columns fixtures through the API.

Acceptance: tests green; the three endpoints documented in the OpenAPI page.

Do not: add update or delete endpoints.

---

## Task 1.5 Streamlit screen

Model: Sonnet.

Goal: a lab manager can use the system without curl.

Reads: API endpoints from 1.2 and 1.4.

Produces:
- `apps/streamlit_app/Home.py`: upload form with metadata fields, result panel showing issues as a table with severity colouring or stored record confirmation, list of recent submissions, buttons to download the validation report as CSV and as HTML.
- `reporting/validation_report.py`: builds the CSV and HTML from a submission and its issues (Jinja template, no inline HTML strings in the app).
- Unit tests for the report builder. README: how to run the app.

Acceptance: app runs against the local API; screenshot described in the report.

Do not: add authentication or multi-page navigation yet.

---

## Task 1.6 End-to-end tests and failure catalogue

Model: Sonnet.

Goal: confidence that the MVP behaves on every fixture and that its limits are written down.

Reads: all of Phase 1.

Produces:
- `tests/workflow/test_intake_end_to_end.py`: for each of the five fixtures, upload through the API, assert status and issue codes, fetch the report.
- `docs/evaluation/intake-mvp.md`: table of fixtures and outcomes, known limitations (encoding, very large files, concurrent uploads, no auth), and what Phase 4 will add.
- Any bug found is fixed in this task.

Acceptance: `make check` green locally and in CI.

Do not: widen scope to fix limitations; list them.

---

## Task 1.7 Evidence package 1 and tag v0.1

Model: Sonnet.

Paste `prompts/evidence-package.md` with N = 1 after the session-start prompt. Then tag `v0.1`, update PROGRESS.md to Phase 2, and before the next session paste `prompts/plan-phase.md` to expand `prompts/phase-2.md`.
