# Progress

Claude reads this file first in every session and updates it at the end of every task. Keep it short. History lives in git and CHANGELOG.md, not here.

## Current phase

Phase 0: repository and environment setup (plan weeks 1-2). Task blocks: `prompts/phase-0.md`.

## Current task

0.4 Track A discovery spec and manifest fixtures. Not started.

## Done

| Task | Date | Commit | Tag |
|---|---|---|---|
| Plan, CLAUDE.md, ADR 0001 | 2026-11-13 | 8310bf7 | |
| Prompt kit, PROGRESS.md | 2026-11-13 | c2809ca | |
| 0.1 Python project skeleton, ADR 0002 | 2026-11-25 | 9babe88 | |
| 0.2 FastAPI app, health endpoint, settings, ADR 0003 | 2026-11-25 | ab8cce4 | |
| 0.3 GitHub Actions CI, README badge | 2026-11-25 | pending push | |

## Next task

0.4. Phase gate: CI green, tag v0.0.1. 0.3 is only fully done once the first Actions run is green; Szonja pastes the result next session.

## Open questions for Szonja

- Mentor conversation (plan section 3): date not yet booked.

## Blockers

None. Waiting on: first GitHub Actions run of `ci.yml` (Szonja pushes, then reports green or red).

## Usage notes

Default model Sonnet 5.5. Record here when a task needed Opus 5.5 and why.

- 0.1 ran on Opus 5.5: task block names Opus because it sets the conventions every later task follows.
- 0.2 ran on Sonnet 5.5 as the block says.
- 0.3 ran on Sonnet 5.5 as the block says.
- Port 8765 on this machine is used by the Job Scout control server; use `--port 8011` (or 8000) for this API.
- Environment: venv + pip (uv not installed); GNU Make 4.4.1 installed via winget on 2026-11-25. Open a new terminal before using `make`.
