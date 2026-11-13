# ADR 0001. Programme shape

**Date:** 2026-11-12
**Status:** accepted

## Context

The original draft planned three loosely coupled projects (document intelligence, four omics pipelines plus multi-omics, and a workflow platform with three case studies) in 520 hours, with the roadmap hopping between them month by month. It did not state which parts Clementine would use or review, used n8n for orchestration, left the LLM choice open, had no CI until week 24 and no buffer.

## Decision

- One monorepo and one platform with three tracks: A (genomics service-provider workflow), B (scientific document intelligence), C (one variant QC and annotation pipeline). Track A orchestrates Track C.
- Each month ends with a tagged release and an evidence package, so the programme is presentable at any month boundary.
- Target roles: life sciences data scientist, AI/NLP/document engineer, automation/BI/workflow. Bioinformatics scientist roles are secondary.
- Main Track A case: genomics service provider (developer's choice). The food and ingredient case is the month 6 reuse demonstration.
- Bioinformatics depth: one pipeline at professional grade (Snakemake, containers, CI, provenance, reference comparison). Other omics are optional months 7-9.
- Engagement: unpaid, Clementine mentor reviews Track B at months 2 and 6.
- Time: 20 hours per week, 6 months core, months 7-9 optional.
- LLM: Claude API through one LLMClient interface, 10-30 EUR per month, Opus 5.5 default with Haiku 5.5 as the measured cost arm.
- CI from week 2, Docker Compose from week 3, deployment fixed in week 24.

## Consequences

- Proteomics, microbiome, multi-omics, pgvector, document comparison and n8n leave the core scope.
- Hand-labelling about 30 papers (roughly 8 hours) is a budgeted task, not an afterthought.
- The service-provider process is an illustrative hypothesis until a validator is found (task in week 13).
