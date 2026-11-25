# Life Sciences AI and Workflow Automation Platform

Portfolio programme, started November 2026. One platform, three tracks:

- **Track A.** Genomics service-provider workflow: submission intake, validation, QC, pipeline execution, draft report, human approval, audit trail.
- **Track B.** Scientific document intelligence: typed extraction from PDFs with page-level provenance, entity extraction, search, question answering with citations, measured against a hand-labelled set.
- **Track C.** One professional-grade variant QC and annotation pipeline in Snakemake, run in CI, with provenance and a reference comparison.

Developed in discussion with Clementine, who mentors and reviews the document-intelligence work. All data is public or synthetic and labelled as such. Nothing here is clinical decision support.

The full plan and roadmap are in [PROJECT_PLAN.md](PROJECT_PLAN.md). The running state is in [PROGRESS.md](PROGRESS.md). Paste-ready session and task prompts are in [prompts/](prompts/README.md). Decisions are recorded in `docs/decisions/`. Monthly evidence packages live in `docs/evidence/`.

## Status

Plan written and committed 2026-11-13. Prompt kit in place. Next: Phase 0 task 0.1 (see PROGRESS.md and prompts/phase-0.md).

## Running locally

Requirements: Python 3.12 and GNU Make. On Windows, Make was installed with `winget install ezwinports.make --source winget` (open a new terminal afterwards so `make` is on the PATH).

Windows (PowerShell), as run on 2026-11-25:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
make install   # editable install plus ruff, mypy, pytest
make check     # lint, type-check, tests
```

Linux or macOS:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
make install
make check
```

Individual targets: `make lint`, `make typecheck`, `make test`. Tool choices are explained in [docs/decisions/0002-python-tooling.md](docs/decisions/0002-python-tooling.md).
