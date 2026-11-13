# Phase 3: genomics pipeline, Track C (plan weeks 9-12)

Reference: PROJECT_PLAN.md section 12.5, section 7, section 9 Month 3, section 13.
Phase gate: Snakemake pipeline runs on a tiny fixture VCF in GitHub Actions; HTML report; provenance manifest; reference comparison with coverage and agreement numbers in `docs/evaluation/`; evidence package 3; tag `v0.3`.
Before task 3.1: paste `prompts/plan-phase.md` once.

## Phase prompt from the plan (section 12.5)

```text
Implement Track C in PROJECT_PLAN.md.

First verify the candidate datasets in section 7.3 (format, metadata, access terms, size) and recommend one with reasons; write the ADR. Recommend Snakemake unless there is a concrete reason for Nextflow; write that ADR too.

Then build the pipeline: VCF validation, QC statistics, config-driven filtering, annotation through a documented Ensembl resource with caching and rate limiting, summary tables, HTML report, provenance manifest (tool versions, parameters, input hashes, accession, retrieval date). Per-rule environments. A tiny fixture must run in GitHub Actions.

Finish with the reference comparison: coverage and agreement with Ensembl's published consequences for a documented variant set, runtime and memory, limitations. Research and educational labelling everywhere. No controlled-access data, no clinical claims.
```

## Task list (to be expanded by plan-phase.md)

| Id | Task | Model |
|---|---|---|
| 3.1 | Dataset verification (1000 Genomes region subset, GIAB HG001, Arabidopsis 1001 Genomes): format, size, access terms; ADR 0005 dataset; ADR 0006 Snakemake vs Nextflow | Opus |
| 3.2 | Download script with checksums, accession, version and retrieval date; `pipelines/variant_annotation/` layout, config schema, tiny fixture VCF (a few hundred records) | Sonnet |
| 3.3 | Rules: validate VCF, `bcftools stats` QC, config-driven filtering; per-rule conda environment; `snakemake --dry-run` in CI | Sonnet |
| 3.4 | Annotation rule: Ensembl VEP REST with caching and rate limiting, or `bcftools csq` with a GFF; decision recorded; fixture run in CI | Opus |
| 3.5 | Summary tables, HTML report (Jinja), provenance manifest (tool versions, params, input hashes) | Sonnet |
| 3.6 | Per-rule tests, Windows note (pipeline runs in WSL or a container; document the local route) | Sonnet |
| 3.7 | Reference comparison on a documented variant set: coverage, agreement with Ensembl consequences, runtime and memory; `docs/evaluation/variant-pipeline.md`; limitations and research-only label | Sonnet |
| 3.8 | Evidence package 3, tag `v0.3` | Sonnet |

## Notes for plan-phase

- Szonja develops on Windows 11. Decide early in 3.2 whether Snakemake runs in WSL2, Docker, or both, and write it down.
- Keep the fixture small enough that the CI run finishes in under five minutes.
