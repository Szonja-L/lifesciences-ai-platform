# Phase 5: data science and evaluation layer (plan weeks 17-20)

Reference: PROJECT_PLAN.md section 12.7, section 8.5, section 9 Month 5, section 13.
Phase gate: KPIs on a 200-submission synthetic batch against a documented simulated baseline; document classification comparison with cross-validation and calibration; one analytical question answered with proper validation; Track B wired into Track A; evidence package 5; tag `v0.5`.
Before task 5.1: paste `prompts/plan-phase.md` once.

## Phase prompt from the plan (section 12.7)

```text
Implement the month 5 data science layer in PROJECT_PLAN.md.

1. Generate a synthetic batch of about 200 submissions with planted errors; define and document the simulated manual baseline; compute the KPIs in section 8.5; build the dashboard.
2. Document classification: TF-IDF + logistic regression vs the LLM, with cross-validation, confusion matrix and calibration on the labelled set.
3. One justified analytical question with proper train/test separation and a limitations note.
4. Route the provider's SOPs and client request documents through Track B extraction and link reports to cited papers.

Report measured results only. Label the baseline as simulated. Do not claim business savings.
```

## Task list (to be expanded by plan-phase.md)

| Id | Task | Model |
|---|---|---|
| 5.1 | Synthetic batch generator: about 200 submissions with planted error types at known rates, seeded and reproducible; stored under `evaluation/batches/` | Sonnet |
| 5.2 | Simulated manual baseline: assumptions written in `docs/evaluation/baseline.md` (minutes per manual check, miss rates) with sources or "assumed" labels | Opus |
| 5.3 | KPI script in `analytics/`: validation pass rate, errors caught, false positives, turnaround, manual intervention rate; results table | Sonnet |
| 5.4 | Dashboard: Plotly in Streamlit (Power BI export optional); KPI page added to the app | Sonnet |
| 5.5 | Document classification: TF-IDF + logistic regression vs LLM on the labelled corpus, stratified cross-validation, confusion matrix, calibration curve; `docs/evaluation/classification.md` | Sonnet |
| 5.6 | One analytical question chosen with Szonja (QC failure prediction from metadata, or variant-burden summaries by group); train and test separation; limitations note | Opus |
| 5.7 | Track B inside Track A: SOP and client-request documents through extraction; report links to cited passages | Sonnet |
| 5.8 | Evidence package 5, tag `v0.5` | Sonnet |

## Notes for plan-phase

- Szonja chooses the question in 5.6 before the session; plan-phase should leave it as a parameter.
- Every number in this phase comes from a script that is in the repository and can be rerun.
