# Progress

Claude reads this file first in every session and updates it at the end of every task. Keep it short. History lives in git and CHANGELOG.md, not here.

## Current phase

Phase 1: submission-intake MVP (plan weeks 3-4). Task blocks: `prompts/phase-1.md`. Phase 0 closed with tag `v0.0.1` on 2026-11-25.

## Current task

1.4 Persist results and read endpoints. Not started.

## Done

| Task | Date | Commit | Tag |
|---|---|---|---|
| Plan, CLAUDE.md, ADR 0001 | 2026-11-13 | 8310bf7 | |
| Prompt kit, PROGRESS.md | 2026-11-13 | c2809ca | |
| 0.1 Python project skeleton, ADR 0002 | 2026-11-25 | 9babe88 | |
| 0.2 FastAPI app, health endpoint, settings, ADR 0003 | 2026-11-25 | ab8cce4 | |
| 0.3 GitHub Actions CI, README badge | 2026-11-25 | 49497cd | |
| 0.4 Track A spec, five manifest fixtures, evaluation/ README | 2026-11-25 | fec1c7d | v0.0.1 |
| 1.1 Postgres (compose), models, Alembic migration 0001, CI service container, ADR 0004 | 2026-11-25 | 90a465e | |
| 1.2 `POST /submissions`, upload storage, ADR 0005 | 2026-11-27 | b1c17c1 | |
| 1.3 Validation engine, rule set v1, ADR 0006 | 2026-11-27 | pending | |

## Next task

1.4 (Sonnet). Call `validate_manifest(path, RULE_SET_V1, today=..., max_rows=...)` after storing the file and save `rule_set.version` with the results. Also in scope there:
- Add the `MAX_MANIFEST_ROWS` setting to config and `.env.example` (the engine takes it as a parameter).
- Decide a cap on header columns or stored issues before inserting them (ADR 0006, limitations).
- If the engine raises, the submission stays `SUBMITTED` and the error is logged (spec section 6).

## Open questions for Szonja

- Mentor conversation (plan section 3): date not yet booked.

## Blockers

None.

## Usage notes

Default model Sonnet 5.5. Record here when a task needed Opus 5.5 and why.

- 0.1 ran on Opus 5.5: task block names Opus because it sets the conventions every later task follows.
- 0.2 ran on Sonnet 5.5 as the block says.
- 0.3 ran on Sonnet 5.5 as the block says.
- 0.4 ran on Opus 5.5: the block names Opus because the whole of Track A rests on this spec.
- 1.1 ran on Opus 5.5: the block names Opus because the data model persists for the whole programme.
- 1.2 ran on Sonnet 5.5 as the block says.
- 1.3 ran on Sonnet 5.5 as the block says.
- DATABASE_URL must use `127.0.0.1`, not `localhost`: on this machine `localhost` tries IPv6 first and stalls (container is IPv4-bound).
- Python start-up on this machine is slow (~8 s per command, likely antivirus scanning `.venv`); not a code issue.
- Docker Desktop stopped once mid-session on 2026-11-25; restart it if DB tests start skipping.
- Fixtures are LF-only via `.gitattributes` (Windows has core.autocrlf=true); upload tests hash them.
- Port 8765 on this machine is used by the Job Scout control server; use `--port 8011` (or 8000) for this API.
- Environment: venv + pip (uv not installed); GNU Make 4.4.1 installed via winget on 2026-11-25. Open a new terminal before using `make`.
