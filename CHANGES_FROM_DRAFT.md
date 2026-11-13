# Changes from the draft plan (2026-11-12)

Assessment of the draft: 7/10 as a document, 4/10 as an executable plan. Principles, boundaries and the prompt pack were kept. The roadmap, scope and stack were reworked.

| Area | Draft | Now | Why |
|---|---|---|---|
| Scope | 3 projects: document intelligence, 4 omics pipelines + multi-omics, platform with 3 case studies | 1 platform, 3 tracks, 1 pipeline, 1 adaptation | 520 hours cannot deliver the draft to a credible standard; one deep pipeline beats four shallow ones |
| Sequencing | Month by month across projects, main deliverable in month 5 | Each month ends with a tagged, demonstrable slice; main platform lands in month 4 | Survives a job offer cutting the programme short |
| Main case | Genomics service provider | Genomics service provider (kept, her choice); food case moved to month 6 as the reuse proof | |
| Bioinformatics | Genomics, transcriptomics, microbiome, proteomics at ~1 week each | One variant QC and annotation pipeline over 4 weeks, in Snakemake, in CI, with reference comparison | Professional-grade evidence; others optional months 7-9 |
| Orchestration | n8n | Snakemake for the pipeline, Python worker + DB state machine for the platform; n8n optional | Postings ask for Snakemake/Nextflow, not n8n |
| LLM | Unspecified | Claude API via one LLMClient; Opus 5.5 default, Haiku 5.5 cost arm measured on the labelled set; cache, cost log, budget cap, prompt versioning, structured outputs, native PDF citations evaluated | Budget control and production-API evidence for AI roles |
| Entity extraction | Model TBD | LLM vs scispaCy baseline on the same labelled spans | A real comparison, not just LLM output |
| Search | Keyword then vectors | Postgres full-text only in core; pgvector optional | ~50 papers do not need vectors |
| CI | Week 24 | GitHub Actions from week 2 | Cheapest strong public signal |
| Containers | Week 24 | Docker Compose from week 3; app image by week 16 | Postgres needs it anyway |
| Deployment | "If feasible" in week 24 | Fixed in week 24 on a free host | A URL on the CV |
| Evaluation | Good list, unscheduled | Labelling budgeted (8 h), 30 papers, 50 Q&A pairs, reference variant set, 200-submission synthetic batch, simulated baseline documented | Numbers that can be quoted |
| Data science | One "baseline ML" week | A full month: KPIs vs baseline, classification comparison with CV and calibration, one justified question, Track B inside Track A | Targets the data scientist roles she chose |
| Evidence | Week 25-26 | Monthly evidence package: tag, demo GIF, LinkedIn post draft, CV bullet drafts | Evidence accumulates |
| Clementine | "May be developed in discussion with" | Unpaid; mentor reviews Track B at months 2 and 6; week 1 conversation about language and sample documents | Named reviewer is CV evidence |
| Validator | None | Week 13 task to find a genomics process validator; process labelled illustrative until then | Honesty and credibility |
| Target roles | Ten | Three families | Sharper choices |
| Buffer | None | Months 7-9 optional, explicit cut order | Realism |
| Prompt pack | 13 phase prompts | 9 phase prompts matching the new roadmap, plus CLAUDE.md with the master instruction | Claude Code reads CLAUDE.md automatically |

Open points to settle during the programme, not now:
- Document language and sample documents from Clementine (week 1 mentor conversation).
- Dataset choice and Snakemake vs Nextflow (week 9 ADRs).
- Whether a genomics process validator can be found (weeks 13-16).
