# ADR 0003: API location and settings

- Status: accepted
- Date: 2026-11-25
- Task: 0.2

## Context

Task 0.2 adds the first runtime code: a FastAPI app and typed configuration. Plan section 5.3 sketches `api/main.py` at the repository root, but ADR 0002 chose a `src` layout, and left the API location open.

## Decisions

**The API lives inside the package: `src/lifesciences_platform/api/main.py`.** A root-level `api/` folder is not part of the installed package, so tests could not import it the way real code does, and mypy (`files = ["src", "tests"]`) would not check it. Inside the package it is installed, typed, tested and importable like everything else. This deliberately differs from the tree in plan section 5.3. Start command: `uvicorn lifesciences_platform.api.main:app --reload`.

**`create_app()` factory plus a module-level `app`.** uvicorn needs a module-level object; tests get a fresh app from the factory, which matters once routers and dependency overrides arrive.

**Settings with pydantic-settings.** One `Settings` class, fields validated at start-up, so a typo such as `LOG_LEVEL=LOUD` fails immediately, not at the first log call. Environment variable names equal the field names (no prefix). A local `.env` is read if present and is git-ignored; `.env.example` documents every variable.

**Secrets are `SecretStr`.** `database_url` (may contain a password) and `anthropic_api_key` print as `**********` in `repr` and logs. Code must call `.get_secret_value()` to use them.

**Optional values are `None`, empty strings count as unset** (`env_ignore_empty=True`). A freshly copied `.env.example` therefore works. `llm_monthly_budget_eur = None` means "not configured"; what the LLMClient does in that case is decided in the LLMClient task, not here.

**`get_settings()` is cached** with `lru_cache`: the environment is read once, not at import time. Tests construct `Settings(_env_file=None)` directly so a developer's own `.env` cannot change results.

**`/health` is liveness only.** It returns status and version and nothing from settings.

## Dependencies added

`fastapi`, `pydantic-settings` (brings `pydantic`), `uvicorn` at runtime; `httpx` for development because FastAPI's `TestClient` requires it. The Pydantic mypy plugin is enabled, as ADR 0002 planned.

## Not decided here

Routers, authentication, CORS, logging set-up, database access, and what the LLMClient does when no budget is configured.
