# Phase 7: hardening and deployment (plan weeks 23-24)

Reference: PROJECT_PLAN.md section 12.9, section 9 Month 6 weeks 23-24, section 15.
Phase gate: fixed benchmark inputs and a full KPI run reported; failure-case catalogue; one public demo URL on Streamlit Community Cloud or a Hugging Face Space with a free hosted Postgres; secrets review done; limitations documented.
Before task 7.1: paste `prompts/plan-phase.md` once.

## Phase prompt from the plan (section 12.9)

```text
Prepare the project for a public demonstration.

Create fixed benchmark inputs, run the full test suite and KPI scripts, and report measured results only. Review correctness and coverage, provenance, secrets, error handling and logging, dependency risks, reproducibility, setup instructions, performance on representative inputs. Catalogue failure cases.

Then propose and implement the smallest safe deployment: Streamlit Community Cloud or a Hugging Face Space with a free hosted Postgres. No confidential data, no private endpoints exposed. Document known limitations.
```

## Task list (to be expanded by plan-phase.md)

| Id | Task | Model |
|---|---|---|
| 7.1 | Benchmark inputs frozen under `evaluation/benchmark/`; full test and KPI run; coverage report; results in `docs/evaluation/benchmark.md` | Sonnet |
| 7.2 | Review pass: error handling, logging, secrets (`.env` never committed, no keys in logs), dependency audit, reproducibility from a clean clone on Windows and Linux | Opus |
| 7.3 | Failure-case catalogue and reliability fixes | Sonnet |
| 7.4 | Deployment: choose host (ADR 0009), free Postgres (Neon or Supabase), demo data seeded, LLM features behind a budget switch or disabled in the public demo, data-retention note | Opus |
| 7.5 | Smoke test of the public URL, README demo link, limitations section | Sonnet |

## Notes for plan-phase

- The public demo must never carry a live API key with an unlimited budget. Prefer disabling LLM calls publicly and showing cached results.
- Third in the cut order. If time is short, 7.1 to 7.3 still happen; 7.4 and 7.5 are dropped with a note.
