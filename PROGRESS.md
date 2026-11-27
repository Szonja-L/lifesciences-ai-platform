# Progress

Claude reads this file first in every session and updates it at the end of every task. Keep it short. History lives in git and CHANGELOG.md, not here.

## Current phase

Phase 1: submission-intake MVP (plan weeks 3-4). Task blocks: `prompts/phase-1.md`. Phase 0 closed with tag `v0.0.1` on 2026-11-25.

## Current task

1.3 Validation engine. Not started.

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
| 1.2 `POST /submissions`, upload storage, ADR 0005 | 2026-11-27 | not committed yet | |

## Next task

1.3 (Sonnet). Pure module, no database or API changes. A 0-byte file reaches it as an accepted submission and must produce `EMPTY_FILE` (decided in 1.2, ADR 0005).

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
- DATABASE_URL must use `127.0.0.1`, not `localhost`: on this machine `localhost` tries IPv6 first and stalls (container is IPv4-bound).
- Python start-up on this machine is slow (~8 s per command, likely antivirus scanning `.venv`); not a code issue.
- Docker Desktop stopped once mid-session on 2026-11-25; restart it if DB tests start skipping.
- Fixtures are LF-only via `.gitattributes` (Windows has core.autocrlf=true); upload tests hash them.
- Port 8765 on this machine is used by the Job Scout control server; use `--port 8011` (or 8000) for this API.
- Environment: venv + pip (uv not installed); GNU Make 4.4.1 installed via winget on 2026-11-25. Open a new terminal before using `make`.
