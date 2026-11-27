# Changelog

All notable changes to this project are recorded here. Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versions follow semantic versioning.

## [Unreleased]

### Added

- Python 3.12 project skeleton: `pyproject.toml` (hatchling build, `src` layout), package `lifesciences_platform` with `common` subpackage, smoke test.
- Tooling: ruff (lint and format), mypy (strict, two relaxations), pytest; `Makefile` targets `install`, `lint`, `typecheck`, `test`, `check`.
- ADR 0002: Python tooling.
- FastAPI app (`lifesciences_platform.api.main`) with `GET /health`, typed `Settings` (pydantic-settings, secrets as `SecretStr`), `.env.example`, unit and integration tests, ADR 0003, README start instructions (task 0.2).
- GitHub Actions CI (`.github/workflows/ci.yml`): `make check` (ruff, strict mypy, pytest) on Ubuntu, Python 3.12, pip cache, for pushes to `main` and pull requests; README badge (task 0.3).
- Track A discovery spec (`docs/architecture/track-a-spec.md`, illustrative): persona, process, manifest schema v1, file rules, issue codes, KPIs, simulated baseline; five synthetic manifest fixtures with expected issues; `evaluation/README.md`; `.gitattributes` keeping fixtures LF (task 0.4).
- PostgreSQL 16 via `docker-compose.yml`; SQLAlchemy 2 models `Submission` and `ValidationResult` with named constraints (status check, unique content hash); `common/db.py`; Alembic with migration 0001; DB tests (rolled back, skipped when unreachable, required in CI via a Postgres service container); ADR 0004 (task 1.1).
- `POST /submissions`: CSV upload with metadata, type and size checks, SHA-256 hash, duplicate refusal (409), files stored outside the repository (`UPLOAD_DIR`); settings `MAX_UPLOAD_BYTES`, `UPLOAD_DIR`; ADR 0005 (task 1.2).
- Manifest validation engine (`common/validation/`): rule set `v1` as data, `validate_manifest` returning typed issues with stable codes, row and column; spec clarified for cases it did not cover; not yet called by the API; ADR 0006 (task 1.3).
