# Interview notes

One block per task, appended by Claude at the end of each session (prompts/session-end.md step 5) and edited by Szonja. Format: task id and title, what was built, why this design, one trade-off, one thing that would break if done differently, one likely interviewer question with a two-sentence answer. Week 26 CV bullets and the LinkedIn write-up are drafted from this file.

## Phase 0

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
