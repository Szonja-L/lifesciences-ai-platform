# ADR 0002: Python tooling

- Status: accepted
- Date: 2026-11-25
- Task: 0.1

## Context

Every later phase builds on the same project layout and quality gates. They must run identically on a Windows laptop and on Ubuntu in GitHub Actions, and be explainable in an interview. Constraint from CLAUDE.md: no dependency without a reason, simple over clever.

## Decisions

**src layout** (`src/lifesciences_platform/`). Tests import the *installed* package, not whatever happens to sit next to them, so packaging mistakes (missing files, wrong package name) fail locally instead of in deployment. Cost: the package must be installed (`pip install -e`) before tests run. `make install` does that.

**hatchling as build backend.** A build backend is required for an editable install. Hatchling is the common modern default and needs one line to find a `src` package. setuptools would also work; nothing here depends on the choice.

**Version in one place.** `pyproject.toml` holds the version; `__init__.py` reads it through `importlib.metadata`. No chance of two numbers drifting apart.

**ruff** for lint and formatting. One fast tool replaces flake8, isort, pyupgrade and black. Rule sets: E, W, F (basic errors), I (imports), B (likely bugs), UP (modern syntax), SIM (simplifications), RUF. Markdown is excluded because ruff 0.17 also formats code blocks inside `.md` files, and the plan and prompts must not be rewritten by a tool.

**mypy, strict mode** over `src` and `tests`. Strict catches missing annotations and `Any` leaking through return values, which matters once LLM output and parsed files flow through typed models. Two checks are relaxed in advance: `disallow_untyped_decorators` (FastAPI route decorators) and `disallow_subclassing_any` (Pydantic, SQLAlchemy and Streamlit base classes when their stubs are incomplete). Everything else in strict stays on. The Pydantic mypy plugin is added when Pydantic arrives (task 0.2).

**pytest** with `--strict-markers` and `--strict-config`, so a typo in a marker or a config key fails instead of being ignored.

**Environment: `venv` + pip.** `uv` was not installed on the development machine on 2026-11-25 (checked with `uv --version`); `venv` and pip ship with Python, so no extra install is needed and CI uses the same commands. Revisit with a new ADR if install time or lock files become a real need.

**Make as the single task runner.** `make install | lint | typecheck | test | check`. Make is preinstalled on GitHub's Ubuntu runners, so CI calls exactly the same targets as the laptop. On Windows it was installed once with `winget install ezwinports.make`. Every recipe is `python -m <tool>`, which runs under both cmd.exe and sh and uses whichever Python environment is active. One tool only: no justfile, no tox, no nox.

## Not decided here

pre-commit, coverage thresholds (`pytest-cov`), Docker, and where the API module lives (task 0.2).
