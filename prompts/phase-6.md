# Phase 6: food and ingredient adaptation (plan weeks 21-22)

Reference: PROJECT_PLAN.md section 12.8, section 8.6, section 9 Month 6.
Phase gate: synthetic supplier specifications and certificates of analysis flow through intake, extraction, unit conversion, material mapping, specification-limit comparison, exceptions and a traceable report; tests for unit conversion and limit logic; no copy of the genomics code.
Before task 6.1: paste `prompts/plan-phase.md` once. This phase is the first in the cut order (plan section 17); if the programme is behind, skip it and say so in PROGRESS.md.

## Phase prompt from the plan (section 12.8)

```text
Adapt the platform to the food and ingredient case in section 8.6 of PROJECT_PLAN.md.

Create synthetic supplier specifications and certificates of analysis as PDFs. Reuse Track B extraction, Track A intake, validation, approval and audit. Add unit conversion, a reviewable material-name mapping table, specification-limit comparison, exception flags, a dashboard and a traceable report. Add tests for unit conversion and specification-limit logic. Do not copy the genomics implementation; show configurability through schemas and processing modules.
```

## Task list (to be expanded by plan-phase.md)

| Id | Task | Model |
|---|---|---|
| 6.1 | Case design: which parts of intake, validation, state machine and reporting are reused unchanged, which are configured, which are new; ADR 0008 on the adaptation mechanism | Opus |
| 6.2 | Synthetic supplier specs and CoAs as PDFs (generated, obviously synthetic supplier names), schema for extraction | Sonnet |
| 6.3 | Unit conversion module and material-name mapping table with review status; tests | Sonnet |
| 6.4 | Specification-limit comparison, exception flags, report; tests | Sonnet |
| 6.5 | Dashboard page and `docs/case-studies/food-adaptation.md` showing what was reused | Sonnet |

## Notes for plan-phase

- Szonja's FrieslandCampina internship is the source of process knowledge here; she validates the process herself. No company data, no real supplier names.
