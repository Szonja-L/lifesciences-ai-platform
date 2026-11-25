# Progress

Claude reads this file first in every session and updates it at the end of every task. Keep it short. History lives in git and CHANGELOG.md, not here.

## Current phase

Phase 0: repository and environment setup (plan weeks 1-2). Task blocks: `prompts/phase-0.md`.

## Current task

Phase 0 gate: push 0.4, confirm CI green, tag `v0.0.1`, then move to Phase 1 task 1.1 (`prompts/phase-1.md`).

## Done

| Task | Date | Commit | Tag |
|---|---|---|---|
| Plan, CLAUDE.md, ADR 0001 | 2026-11-13 | 8310bf7 | |
| Prompt kit, PROGRESS.md | 2026-11-13 | c2809ca | |
| 0.1 Python project skeleton, ADR 0002 | 2026-11-25 | 9babe88 | |
| 0.2 FastAPI app, health endpoint, settings, ADR 0003 | 2026-11-25 | ab8cce4 | |
| 0.3 GitHub Actions CI, README badge | 2026-11-25 | 49497cd | |
| 0.4 Track A spec, five manifest fixtures, evaluation/ README | 2026-11-25 | (fill after commit) | |

## Next task

Phase gate, then 1.1 PostgreSQL, data models, first migration (Opus). Gate: CI green on the 0.4 push, `git tag v0.0.1 -m "tooling, CI, health endpoint, Track A spec"`, push the tag.

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
- Phase 1 task 1.1 renumbered its ADR to 0004 (0003 is already the API/settings ADR).
- Fixtures are LF-only via `.gitattributes` (Windows has core.autocrlf=true); upload tests hash them.
- Port 8765 on this machine is used by the Job Scout control server; use `--port 8011` (or 8000) for this API.
- Environment: venv + pip (uv not installed); GNU Make 4.4.1 installed via winget on 2026-11-25. Open a new terminal before using `make`.
