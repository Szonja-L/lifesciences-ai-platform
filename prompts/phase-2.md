# Phase 2: document intelligence, Track B (plan weeks 5-8)

Reference: PROJECT_PLAN.md section 12.4, section 6, section 5.4 (LLM usage rules), section 9 Month 2, section 13.
Phase gate: measured field-level precision, recall and F1 on 30 hand-labelled papers; LLM vs scispaCy entity comparison; 50 hand-judged Q&A pairs with citation correctness; mentor review 1 notes in `docs/evidence/`; evidence package 2; tag `v0.2`.
Before task 2.1: paste `prompts/plan-phase.md` once to expand this list into detailed task blocks against the real repository. Before task 2.3: a Claude API key exists, a spend limit is set in the Anthropic console, and the key is in `.env` only.

## Phase prompt from the plan (section 12.4)

```text
Implement Track B in PROJECT_PLAN.md incrementally.

1. Download script for the CC-BY corpus with checksums; PyMuPDF extraction with page-level provenance.
2. Pydantic schema for a scientific paper with unknown values and source page per field.
3. LLMClient over the official anthropic SDK: structured outputs via messages.parse(), response cache keyed by content hash + model + prompt version, per-call cost log, LLM_MONTHLY_BUDGET_EUR cap, prompt files under version control. Default model from config (claude-opus-5-5), with claude-haiku-5-5 as the comparison arm.
4. Evaluation script for field-level precision, recall and F1 against evaluation/papers/labels.jsonl.
5. Entity extraction with a scispaCy baseline and the same evaluation.
6. PostgreSQL full-text search, then question answering with document and page citations. Evaluate native PDF citations against chunk retrieval on the 50 Q&A pairs.
7. Streamlit pages: upload, record with page references, search, ask, inspect evidence, export.

Do not build a generic chatbot. Never invent references. State the cost and privacy implications of every external call before adding it. Report measured numbers only.
```

## Task list (to be expanded by plan-phase.md)

| Id | Task | Model |
|---|---|---|
| 2.1 | Corpus: choose 40-50 CC-BY papers (plant genomics or photosynthesis), download script with checksums, licence file, `data/README.md` | Sonnet |
| 2.2 | PyMuPDF ingestion: `documents` and `document_pages` tables, text per page, scanned-PDF detection documented as unsupported | Sonnet |
| 2.3 | `LLMClient` in `common/llm/`: anthropic SDK, structured outputs, cache, cost log table, monthly budget cap, prompt files with versions, explicit stop_reason handling; ADR 0004 | Opus |
| 2.4 | Paper schema (Pydantic, `unknown` allowed, source page per field) and extraction over the corpus with Opus 5.5; Message Batches for the bulk run | Sonnet |
| 2.5 | Labelling tooling: a Streamlit or CSV workflow for Szonja to label 30 papers (about 8 hours of her time, scheduled across weeks 6-7), stored in `evaluation/papers/labels.jsonl` | Sonnet |
| 2.6 | Evaluation script: field-level precision, recall, F1; Opus 5.5 vs Haiku 5.5 arm with cost; results in `docs/evaluation/extraction.md` | Sonnet |
| 2.7 | Entity extraction: LLM spans vs scispaCy baseline, same labelled spans, page and offset stored | Sonnet |
| 2.8 | Postgres full-text search and grounded Q&A with document and page citations; 50 Q&A pairs judged by Szonja; native PDF citations vs chunk retrieval compared | Opus |
| 2.9 | Streamlit pages: search, ask, inspect evidence, export; mentor review 1 held and notes saved | Sonnet |
| 2.10 | Evidence package 2, tag `v0.2` (`prompts/evidence-package.md`, N = 2) | Sonnet |

## Notes for plan-phase

- Clementine mentor conversation outcome (document language, sample documents) may change 2.1. Check `docs/evidence/mentor-notes.md` first.
- Budget: the whole phase should stay under 30 EUR of API spend. The cost log from 2.3 is the evidence.
