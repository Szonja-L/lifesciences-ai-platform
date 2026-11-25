# Progress

Claude reads this file first in every session and updates it at the end of every task. Keep it short. History lives in git and CHANGELOG.md, not here.

## Current phase

Phase 0: repository and environment setup (plan weeks 1-2). Task blocks: `prompts/phase-0.md`.

## Current task

0.3 Continuous integration. Not started.

## Done

| Task | Date | Commit | Tag |
|---|---|---|---|
| Plan, CLAUDE.md, ADR 0001 | 2026-11-13 | 8310bf7 | |
| Prompt kit, PROGRESS.md | 2026-11-13 | c2809ca | |
| 0.1 Python project skeleton, ADR 0002 | 2026-11-25 | 9babe88 | |
| 0.2 FastAPI app, health endpoint, settings, ADR 0003 | 2026-11-25 | (fill in after commit) | |

## Next task

0.3, then 0.4. Phase gate: CI green, tag v0.0.1.

## Open questions for Szonja

- Mentor conversation (plan section 3): date not yet booked.

## Blockers

None.

## Usage notes

Default model Sonnet 5.5. Record here when a task needed Opus 5.5 and why.

- 0.1 ran on Opus 5.5: task block names Opus because it sets the conventions every later task follows.
- 0.2 ran on Sonnet 5.5 as the block says.
- Port 8765 on this machine is used by the Job Scout control server; use `--port 8011` (or 8000) for this API.
- Environment: venv + pip (uv not installed); GNU Make 4.4.1 installed via winget on 2026-11-25. Open a new terminal before using `make`.
