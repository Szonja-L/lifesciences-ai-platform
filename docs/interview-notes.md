# Interview notes

One block per task, appended by Claude at the end of each session (prompts/session-end.md step 5) and edited by Szonja. Format: task id and title, what was built, why this design, one trade-off, one thing that would break if done differently, one likely interviewer question with a two-sentence answer. Week 26 CV bullets and the LinkedIn write-up are drafted from this file.

## Phase 1

### 1.4 Persist results and read endpoints (2026-11-27)

- Built: validation on upload with stored issues and rule set version, a paginated list and a detail endpoint, a 50-column input limit, ADR 0007.
- Why: the upload commits as `SUBMITTED` first and the results go in a second transaction, so a crash leaves an honest state and never partial results or a false "valid".
- Trade-off: validation runs inside the request, which needs no queue or worker, but a submission stuck at `SUBMITTED` cannot yet be re-run.
- Would break otherwise: with one transaction, an engine crash would roll the submission away, and the client's upload would leave no trace for staff to follow up.
- Interviewer question: "Why return 201 when validation crashed?" The submission was accepted and stored, so a 5xx would invite a retry that is refused as a duplicate. The status in the body says it is not validated, and the log names the submission without quoting client data.

### 1.3 Validation engine (2026-11-27)

- Built: rule set `v1` as data, a pure `validate_manifest` that returns typed issues with stable codes, row and column, tests on all five fixtures, ADR 0006.
- Why: what is valid (rules) is separate from how to check (engine), and the validation date is passed in, so the same file and rule version always give the same result.
- Trade-off: rules are Python dataclasses rather than YAML, so mypy checks them and no loader is needed, but a rule change is a code change.
- Would break otherwise: converting before checking the format would accept `nan` or `1e2` as a DNA concentration, because Python's number parser allows them.
- Interviewer question: "How do you handle a malformed file?" File-level faults return one clear issue and stop, while header and cell faults are all collected so the client can fix everything in one pass. A file that cannot be opened raises instead, so a system fault is never blamed on the client's data.

### 1.2 File upload endpoint (2026-11-27)

- Built: `POST /submissions` with extension, content-type and size checks, SHA-256 hashing, hash-named storage outside the repository, a `SUBMITTED` row, clear 4xx/503 errors, ADR 0005.
- Why: intake rules are plain Python that raises typed errors and the route only maps them to HTTP, so the rules are testable without a server and reusable by another front end.
- Trade-off: files go to local disk, which is simple to run and inspect but ties the service to one machine until storage moves to an object store.
- Would break otherwise: checking "does this hash exist?" before inserting lets two simultaneous uploads both pass; relying on the unique constraint at flush time cannot.
- Interviewer question: "How do you keep the database and the file system consistent?" I flush the row, write the file with an atomic rename, then commit, so a failed write rolls the row back. The worst case is a stray file named by its own hash, which does no harm.

### 1.1 PostgreSQL, data models, first migration (2026-11-25)

- Built: Postgres 16 in Docker Compose, typed SQLAlchemy 2 models for submissions and validation results, Alembic migration 0001, database tests that roll back, a Postgres service container in CI, ADR 0004.
- Why: the database enforces the rules that must never break (unique file hash, allowed status, valid row numbers), so a bug in API code cannot store a duplicate upload or an unknown state.
- Trade-off: status is a VARCHAR with a named check constraint instead of a native Postgres ENUM; each new phase widens it with a small migration, in exchange for changes that are plain SQL and reversible.
- Would break otherwise: without the constraint naming convention, Postgres invents constraint names and a later migration that widens the status check could not reliably find the constraint to drop.
- Interviewer question: "How do you know your migrations match your models?" A test runs `alembic check` against the migrated database, which fails if a model changed without a migration. CI sets REQUIRE_DB=1 so that test cannot be silently skipped.

## Phase 0

### 0.4 Track A discovery spec and manifest fixtures (2026-11-25)

- Built: an illustrative requirements spec for a sequencing-service intake workflow (persona, process, manifest schema v1, 14 stable issue codes, KPIs, simulated baseline) and five synthetic fixtures whose expected issues are written down row by row.
- Why: the spec answers "what is a valid manifest" before any code exists, so the Phase 1 validator, upload endpoint and tests all build against one written contract instead of against each other.
- Trade-off: a small 9-column schema exercises every issue code but is simpler than a real provider's manifest; I kept it small and labelled the whole process as an unvalidated hypothesis.
- Would break otherwise: without `.gitattributes`, Windows checks the fixtures out with CRLF and CI with LF, so the same file would hash differently and duplicate-upload tests would pass on one machine and fail on the other.
- Interviewer question: "How do you claim business value without a real client?" I define a simulated manual baseline with every assumption stated and shown at a low and a high value, and label it simulated wherever it appears. I report measured detection rates on planted errors, never invented savings.

### 0.3 Continuous integration (2026-11-25)

- Built: one GitHub Actions workflow that installs the package and runs `make check` (ruff, strict mypy, pytest) on Ubuntu with Python 3.12, for pushes to `main` and every pull request, plus a README badge.
- Why: the workflow calls the same Makefile target I run locally, so a green local check and a green CI run mean the same thing, and the CI file stays about 30 lines.
- Trade-off: one combined step gives a less granular view than three separate steps, in exchange for no drift between local and CI commands.
- Would break otherwise: if CI listed the tool commands itself, adding a check to the Makefile (say a Snakemake dry run) would pass locally but never run in CI.
- Interviewer question: "How do you keep CI cheap and safe?" Read-only token permissions, no secrets, pip cache keyed on `pyproject.toml`, a 15-minute timeout and cancellation of superseded runs. Nothing in CI can publish or deploy.

### 0.2 FastAPI app, health endpoint, settings (2026-11-25)

- Built: a FastAPI app with `GET /health` (status + package version), a typed `Settings` class read from environment variables, `.env.example`, 11 new tests, ADR 0003.
- Why: configuration is validated once at start-up and secrets are `SecretStr`, so a bad `LOG_LEVEL` fails immediately and a key or database password never appears in a log line.
- Trade-off: the API sits inside the installed package instead of the root `api/` folder drawn in the plan, in exchange for it being imported, type-checked and tested like all other code.
- Would break otherwise: if empty values in `.env.example` were not treated as unset, copying the file would crash start-up on the empty budget number.
- Interviewer question: "Why a `create_app()` factory?" Tests and later routers each get a fresh app with no shared state, while uvicorn still gets the module-level `app` it needs.

### 0.1 Python project skeleton (2026-11-25)

- Built: installable Python 3.12 package in a `src` layout, ruff + strict mypy + pytest, one `Makefile` whose `make check` runs all three, ADR 0002.
- Why: the same five commands run on Windows and in CI, so "works on my machine" and "works in CI" mean the same thing.
- Trade-off: `src` layout forces an install before tests run (`pip install -e`), in exchange for tests importing the real installed package.
- Would break otherwise: with a flat layout, tests could pass by importing local files that never make it into the built package, and the bug only shows up on deployment.
- Interviewer question: "Why strict mypy on a portfolio project?" Strict mode stops untyped data, including parsed CSVs and LLM output later, from silently spreading as `Any`. I relaxed only the two checks that clash with FastAPI and Pydantic decorators and base classes, and wrote down why in an ADR.
