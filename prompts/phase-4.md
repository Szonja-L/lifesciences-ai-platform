# Phase 4: workflow platform core, Track A (plan weeks 13-16)

Reference: PROJECT_PLAN.md section 12.6, sections 8.3 to 8.5, section 9 Month 4, section 14.
Phase gate: a synthetic submission goes from upload to approved report through the state machine and the real pipeline; tests for success, invalid submission, QC failure, pipeline failure, rejection; app Docker image; evidence package 4; tag `v0.4`.
Before task 4.1: paste `prompts/plan-phase.md` once. This is the main deliverable; expect 8-9 tasks.

## Phase prompt from the plan (section 12.6)

```text
Implement the Track A platform core in PROJECT_PLAN.md using the intake, validation and pipeline components that already exist.

Build: submission state machine with the states in section 8.3, exception queue, audit-trail table, versioned metadata schema, background worker that runs the Snakemake pipeline per submission with log capture, failure handling and retry, draft report from pipeline outputs, approve/reject with comments, final package download, provenance chain from upload to report, dashboard for status and exceptions.

Add tests for success, invalid submission, QC failure, pipeline failure, rejection. Build the app Docker image. Keep business logic in tested Python modules.
```

## Task list (to be expanded by plan-phase.md)

| Id | Task | Model |
|---|---|---|
| 4.1 | State machine module with the states in section 8.3, allowed transitions as data, transition function with audit-trail write; ADR 0007 | Opus |
| 4.2 | Audit-trail table, versioned metadata schema, migration; exception queue view | Sonnet |
| 4.3 | Worker loop: polls for `QC_PASSED`, runs the Snakemake pipeline per submission in a subprocess or container, captures logs, sets `RUNNING`, `ANALYSED` or `PIPELINE_FAILED`, retry policy | Opus |
| 4.4 | QC step between validation and pipeline using the pipeline's QC rule outputs; `QC_FAILED` path | Sonnet |
| 4.5 | Draft report from pipeline outputs (reuse Phase 3 report) attached to the submission; `DRAFT_REPORT` state | Sonnet |
| 4.6 | Reviewer approve or reject with comments; final package download (report, provenance manifest, audit extract); provenance chain documented | Sonnet |
| 4.7 | Dashboard pages: status board, exception queue, submission detail with audit timeline | Sonnet |
| 4.8 | Workflow tests for the five scenarios; app Dockerfile and compose service; `docs/architecture/platform.md` with a diagram | Sonnet |
| 4.9 | Evidence package 4, tag `v0.4` | Sonnet |

## Notes for plan-phase

- Week 13 side task for Szonja, not for Claude: find one genomics or sequencing-service contact to sanity-check the process (WUR facility, a commercial provider). Outcome goes in `docs/evidence/validator.md`. Until then, every page says "illustrative process".
- Keep the worker simple: a loop in a process, no queue library, unless a concrete problem forces it. Say so in the ADR.
