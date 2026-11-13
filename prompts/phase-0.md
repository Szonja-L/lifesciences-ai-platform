# Phase 0: repository and environment setup (plan weeks 1-2)

Reference: PROJECT_PLAN.md section 12.2, section 5.3 (repository structure), section 5.2 (stack).
Phase gate: ruff, mypy and pytest green in GitHub Actions; `v0.0.1` tagged; PROGRESS.md points at Phase 1.
Out of scope for the whole phase: PostgreSQL, Docker, the Claude API, Snakemake, Streamlit.

Paste one task block per session, after `prompts/session-start.md`.

---

## Task 0.1 Python project skeleton

Model: Opus (first task of the phase, sets conventions everything else follows).

Goal: a Python 3.12 project that installs, lints, type-checks and runs one passing test, with the conventions written down.

Reads: PROJECT_PLAN.md sections 5.2 and 5.3; .gitignore.

Produces:
- `pyproject.toml` with project metadata, dependencies kept minimal (nothing beyond what this task needs), ruff config, mypy config (strict enough to catch missing annotations, not so strict that FastAPI later fights it), pytest config with `tests/` as root and `src` layout.
- `src/lifesciences_platform/__init__.py` with a version string, and `src/lifesciences_platform/common/__init__.py`.
- `tests/unit/test_smoke.py` that imports the package and checks the version.
- A `Makefile` with `install`, `lint`, `typecheck`, `test`, `check` (all three). One tool for this, not a Makefile and a justfile.
- `CHANGELOG.md` with an "Unreleased" section.
- `docs/decisions/0002-python-tooling.md`: why ruff, mypy, pytest, src layout, and which environment tool (recommend `uv` if installed, otherwise `venv` + pip; check and say which).
- README "Running locally" filled in with the exact commands that were run.

Acceptance: `make check` passes locally; output pasted in the report.

Do not: add FastAPI, pre-commit, Docker or any application module yet. Do not create empty folders for later tracks.

---

## Task 0.2 FastAPI app, health endpoint, settings

Model: Sonnet.

Goal: a running API with a health endpoint and typed settings loaded from the environment.

Reads: PROJECT_PLAN.md section 5.3 (where `api/` and `common/` sit); task 0.1 outputs.

Produces:
- `src/lifesciences_platform/common/config.py` with a pydantic-settings `Settings` class: `app_env`, `log_level`, and placeholders for `database_url`, `anthropic_api_key`, `llm_monthly_budget_eur` with safe defaults or `None`.
- `.env.example` listing every setting with a comment and no real values.
- `api/main.py` (or `src/lifesciences_platform/api/main.py`, follow the layout decided in 0.1 and say which) creating the FastAPI app with `GET /health` returning `{"status": "ok", "version": ...}`.
- `tests/unit/test_config.py` (settings load from env, defaults work) and `tests/integration/test_health.py` using `TestClient`.
- README: how to start the API with uvicorn.

Acceptance: `make check` green; `uvicorn ... --reload` serves `/health`; both pasted.

Do not: add routers, database code, auth or CORS beyond the default.

---

## Task 0.3 Continuous integration

Model: Sonnet.

Goal: every push and pull request runs ruff, mypy and pytest on GitHub Actions.

Reads: Makefile, pyproject.toml.

Produces:
- `.github/workflows/ci.yml`: Ubuntu, Python 3.12, cached dependency install, `make check`. Triggers on push to `main` and on pull requests.
- README: CI badge and one line on what CI runs.
- CHANGELOG entry.

Acceptance: after I push, the Actions run is green. Claude cannot see GitHub, so it reports "ready to push"; I paste the run result back or confirm it in the next session.

Do not: add release workflows, Docker builds or secrets to CI.

---

## Task 0.4 Track A discovery spec and manifest fixtures

Model: Opus (this is the requirements document the whole of Track A rests on).

Goal: a written, illustrative specification of the service-provider workflow and the five synthetic sample manifests that Phase 1 validates.

Reads: PROJECT_PLAN.md sections 8.1 to 8.5 and the Week 1 bullets of section 9; `docs/evidence/mentor-notes.md` if it exists.

Produces:
- `docs/architecture/track-a-spec.md`: persona (lab manager at a small sequencing service), current illustrative process, proposed process, inputs (sample manifest CSV plus submission metadata), outputs, exception cases, approval points, KPIs, simulated manual baseline definition. Labelled "illustrative, not validated with a service provider" at the top. Includes the manifest schema as a table: column, type, required, allowed values, example.
- `tests/fixtures/manifests/` with five CSV files: `valid.csv`, `missing_columns.csv`, `invalid_values.csv`, `empty.csv`, `unsupported_type.txt`, plus a `README.md` saying what each one is meant to trigger. All values synthetic and obviously so (sample ids like `S-0001`, no real names).
- `evaluation/README.md` explaining that labelled sets and synthetic batches live here.

Acceptance: the spec answers, for Phase 1, "what is a valid manifest" without further questions. `make check` still green.

Do not: write validation code. Do not invent regulatory claims; keep the process generic.

---

## Phase gate

After 0.4: confirm CI green on the latest push, tag `v0.0.1` ("tooling, CI, health endpoint, Track A spec"), update PROGRESS.md to Phase 1 task 1.1. Then open `prompts/phase-1.md`.
