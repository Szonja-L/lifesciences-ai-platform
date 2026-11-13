# Life Sciences AI and Workflow Automation Portfolio Programme

**Project plan and implementation brief for Claude Code**
**Duration:** 26 weeks core (months 1-6), up to 13 optional weeks (months 7-9)
**Effort:** about 20 hours per week, roughly 520 hours core
**Setting:** unpaid portfolio programme developed in discussion with Clementine (analytics, text mining and document-processing company), who mentor and review the document-intelligence work
**Written:** 2026-11-12. Replaces the draft "Six-Month AI, Bioinformatics and Life Sciences Automation Portfolio Programme". See `CHANGES_FROM_DRAFT.md`.

---

## 1. Executive summary

One monorepo, one platform, three tracks. The tracks are sequenced so that **every month ends with a finished, demonstrable, tagged slice**. If a job offer cuts the programme short at any month boundary, what exists is still complete and presentable.

| Track | What it is | Which roles it targets |
|---|---|---|
| **A. Genomics service-provider workflow platform** | Submission intake, validation, QC, pipeline execution, draft report, human approval, audit trail, dashboard | Automation, BI and workflow roles; life-sciences data roles |
| **B. Scientific document intelligence** | PDF extraction into typed, validated records with page-level provenance; entity extraction; search; question answering with citations; a labelled evaluation set | AI, NLP and document-engineering roles |
| **C. One professional-grade genomics pipeline** | Variant QC and annotation in Snakemake with containers, CI, provenance and a reference comparison. Track A orchestrates it | Credibility for bioinformatics-adjacent data roles |
| **Data science layer** (month 5) | Measured process KPIs on a synthetic batch against a documented simulated baseline; one statistical or ML comparison with proper validation; dashboards | Life-sciences data scientist roles |
| **Food and ingredient adaptation** (month 6) | Supplier specifications and certificates of analysis through extraction, unit conversion, material mapping and specification checks, reusing Track A and B components | Proves reuse; carries the FrieslandCampina domain story |

**Deliberately out of core scope** (optional months 7-9 only): proteomics, microbiome, multi-omics integration, a second pipeline, pgvector semantic search, document comparison, n8n integrations.

The programme is still ambitious. The objective is a small number of well-engineered, tested, measured and documented end-to-end workflows, not breadth.

### Intended outcomes at month 6

- A public GitHub repository with green CI, Docker Compose setup, tests and a decision log.
- Track B application with structured extraction, measured field-level precision and recall on a hand-labelled set, search and citation-backed answers, reviewed twice by the Clementine mentor.
- Track C pipeline that runs in CI on a fixture, with a provenance manifest and a documented comparison against a public reference.
- Track A end-to-end: submission to approved report, with every state, action and timestamp in an audit trail.
- A KPI report comparing the automated workflow with a documented simulated baseline.
- One deployed public demo.
- Three case studies, architecture diagrams, short demo videos, six monthly evidence packages, CV bullets and a LinkedIn write-up based only on what was built and measured.

---

## 2. Personal and career context

Build on existing strengths rather than starting as a beginner:

- MSc Bioinformatics, Wageningen University; BSc Molecular Genetics and Biotechnology.
- MSc research: phylogenomic analyses of photosynthesis-related genes across hundreds of angiosperm genomes (Linux cluster, SLURM).
- Industry internship at FrieslandCampina: Power BI, Power Query and DAX nutrient-monitoring model on raw-material data and SAP product specifications, including data quality, unit conversion, monitoring metrics and R&D stakeholder communication.
- Working knowledge of Python, R, SQL, Power BI, Git and GitHub, APIs, introductory machine learning. Nextflow, Snakemake, Docker, Singularity and CI used in courses.
- Experienced user of AI coding assistants (Claude Code, ChatGPT).

### Target roles (decided 2026-11-12)

1. Life sciences data scientist / biotech data scientist
2. AI engineer, NLP or document-intelligence engineer, AI implementation specialist
3. Automation, BI and workflow roles in life sciences, food or industrial biotechnology

Bioinformatics scientist roles are secondary. Track C gives credibility there without consuming the programme.

The portfolio must show domain knowledge and transferable engineering together. Do not present the work as academic analysis or as a collection of chatbots.

---

## 3. Collaboration context and boundaries

Clementine's public-facing work covers analytics, data science, NLP and text analytics, document processing, network analysis, consulting and software. A Clementine mentor reviews Track B at the end of month 2 and month 6 and may give a reference.

Rules:

- Do not assume the company's website describes everything it does internally.
- Do not assume the company has approved any use case, dataset, architecture or client engagement.
- Start with synthetic and public datasets. Use internal or client data only after explicit approval and under agreed security, privacy and contractual terms.
- Never place confidential client data, credentials, proprietary documents or personal data in a public repository, public demo, prompt, external LLM call or case study without explicit authorisation.
- Label synthetic demonstrations as synthetic. Never claim a prototype was used by a client or produced savings unless measured and approved.
- Tool choices follow technical suitability, maintainability, cost and learning value, not Clementine's current stack.

**Week 1 mentor conversation** (30 minutes, written notes kept in `docs/evidence/mentor-notes.md`): what they would like to see from the document-intelligence track, document language (Hungarian, English or both), whether any non-confidential sample documents can be shared, and when the two review sessions happen.

---

## 4. Programme design principles

### 4.1 Vertical slices
One small workflow working from input to output beats many incomplete modules. Expand only after the full path works.

### 4.2 Common foundation, no premature abstraction
Implement a working use case first; extract shared components when a second use case needs them.

### 4.3 Traceable outputs
Every scientific or business output keeps provenance: input file and hash, source record, processing step, software version, parameters, timestamp, validation result, references. AI-generated answers separate sourced facts from interpretation.

### 4.4 Human in the loop
Consequential actions, uncertain extractions, failed QC and report release require human review. Nothing in this programme diagnoses, recommends treatment or acts as clinical decision support.

### 4.5 Measure whether it works
Every major workflow has tests and a measured evaluation. A polished dashboard is not evidence.

### 4.6 Controlled scope
Add a library or framework only when it solves a defined problem. Follow the cut order in section 17 when behind.

### 4.7 AI coding assistants are collaborators, not authorities
Claude Code inspects before changing, explains architectural decisions, writes and runs tests, reports real results and avoids large unreviewed changes. The developer must be able to explain every data flow in an interview.

### 4.8 Monthly evidence package (new)
In the last two hours of every month: tag a release, update the README, record a 60-second demo GIF or video, draft one LinkedIn post and one or two CV bullets, and write `docs/evidence/month-N.md` listing what was built, what was measured and what was cut. Evidence accumulates monthly; it never waits for week 25.

---

# PART I. PLATFORM AND TRACK DEFINITIONS

## 5. Shared platform architecture

### 5.1 Logical architecture

```text
                 User / reviewer / analyst
                            |
                   Streamlit application
                            |
                       FastAPI API
                            |
       +--------------------+--------------------+
       |                    |                    |
  Document services   Pipeline services    Workflow services
  - PDF text + pages  - Snakemake runner   - submission state machine
  - LLM extraction    - QC + annotation    - exception queue
  - entity extraction - provenance         - approvals
  - search / Q&A      - reports            - audit trail
       |                    |                    |
       +--------------------+--------------------+
                            |
                  PostgreSQL + file storage
                            |
                 Public data: PMC OA, Ensembl,
                 1000 Genomes or equivalent
```

### 5.2 Stack

| Area | Choice | Notes |
|---|---|---|
| Language | Python 3.12 | R only inside the pipeline where Bioconductor is the right tool (not needed in core) |
| API | FastAPI + Pydantic v2 | Typed contracts, generated docs |
| Database | PostgreSQL via Docker Compose from week 3 | SQLAlchemy 2 + Alembic migrations |
| Search | PostgreSQL full-text search | pgvector only in optional months |
| Frontend | Streamlit | Fast, good enough for a portfolio demo |
| Pipeline manager | **Snakemake** | Python-native, CI-testable on a tiny fixture. Nextflow is the alternative if a target posting demands it; decide in week 9 and record an ADR |
| Job execution | FastAPI background worker loop + DB state machine | No queue library until a measured need appears |
| LLM | **Claude API via the official `anthropic` SDK**, one `LLMClient` interface | See 5.4 |
| PDF parsing | PyMuPDF | Page-level text; scanned PDFs documented as unsupported |
| Entity baseline | scispaCy | Rule or model baseline to compare against LLM extraction |
| ML and stats | scikit-learn, SciPy, statsmodels | Interpretable baselines only |
| Visualisation | Plotly in Streamlit; Power BI for the KPI dashboard if useful | |
| Testing | pytest, pytest-cov | Unit, integration, workflow, pipeline fixture tests |
| Quality | ruff, mypy | Run in CI |
| CI | **GitHub Actions from week 2** | lint, type-check, tests, Snakemake dry-run |
| Containers | Docker Compose (Postgres from week 3, app image by week 16) | |
| Deployment | Streamlit Community Cloud or Hugging Face Space + Neon or Supabase free Postgres | Week 24, fixed |

Not in this programme: microservices, Kubernetes, agent frameworks, custom model training, n8n in core, multiple frontends, Neo4j.

### 5.3 Repository structure

```text
lifesciences-ai-platform/
├── README.md
├── PROJECT_PLAN.md
├── CHANGELOG.md
├── pyproject.toml
├── .env.example
├── .gitignore
├── docker-compose.yml
├── .github/workflows/ci.yml
├── docs/
│   ├── architecture/
│   ├── decisions/          # ADRs, one per architectural choice
│   ├── evaluation/         # measured results, test-set descriptions
│   ├── evidence/           # monthly evidence packages, mentor notes
│   └── case-studies/
├── apps/streamlit_app/
├── api/main.py
├── src/lifesciences_platform/
│   ├── common/             # config, logging, storage, validation, provenance, llm
│   ├── documents/          # Track B
│   ├── workflows/          # Track A state machine, worker, approvals, audit
│   ├── reporting/
│   └── analytics/          # month 5 KPIs and comparisons
├── pipelines/variant_annotation/   # Track C: Snakefile, config, envs, fixture
├── evaluation/             # labelled sets, Q&A pairs, reference sets, synthetic batches
├── tests/{unit,integration,workflow,fixtures}/
├── data/{README.md,synthetic,samples}/
└── scripts/                # download scripts with checksums
```

Never commit raw datasets, restricted data, secrets, private documents or bulky generated outputs. Commit download scripts with checksums instead.

### 5.4 LLM usage rules

- One interface, `LLMClient`, wraps the official Anthropic Python SDK. Nothing else in the codebase imports the SDK directly.
- Default model `claude-opus-5-5` for extraction quality. `claude-haiku-5-5` is the cost arm: both are run on the labelled evaluation set and the measured difference decides what the bulk path uses. Model ids live in config, never in code.
- Structured outputs through the SDK's `messages.parse()` with the Pydantic schema for the document type, so the SDK validates the response against the schema.
- For page citations, evaluate the API's native PDF document input with citations enabled (returns page locations) against chunk-based retrieval, and record which gives better citation correctness.
- Responses cached in Postgres keyed by content hash, model id and prompt version. Re-runs cost nothing.
- Every call logs input tokens, output tokens, model and cost. `LLM_MONTHLY_BUDGET_EUR` in `.env` caps spend; the client refuses calls past the cap. Target 10-30 EUR per month. At this scale (about 50 papers, roughly 15K tokens each) one full Opus pass costs a few euros.
- Use the Message Batches endpoint for bulk re-processing when latency does not matter; it halves cost.
- Prompt versions are files under `src/lifesciences_platform/common/llm/prompts/` and are part of provenance.
- Handle `stop_reason` values explicitly, including refusals and `max_tokens`. Never silently fill missing fields; unknown stays unknown.

---

## 6. Track B: scientific document intelligence

### 6.1 Purpose
Turn scientific PDFs into searchable, structured, traceable records. The differentiator is **reliable extraction with evidence traceability and measured accuracy**, not summarisation.

### 6.2 Corpus
40-50 open-access papers from the PubMed Central Open Access subset with a CC-BY licence, in plant genomics and photosynthesis so the developer can label them credibly. Download script with accession list and checksums. If the Clementine mentor can share non-confidential sample documents of their own type, a second small corpus may be added in month 5 or later.

### 6.3 Capabilities (core)
1. Upload a PDF; validate type and size.
2. Extract text with page-level provenance; store per page.
3. Extract typed fields into a validated record: title, authors, year, organisms, techniques, data accessions, key findings, each with source page and the value `unknown` allowed.
4. Extract entities: genes, organisms, techniques. LLM extraction compared against a scispaCy baseline on the labelled set.
5. Keyword search over the collection (PostgreSQL full-text).
6. Answer a question from retrieved passages with citations (document, page). Show the cited passage so the reviewer can check it.
7. Export records to JSON or CSV.
8. Processing history, prompt version, model id and cost per document.

Deferred to optional months: document comparison, pgvector semantic search, a second document type unless the mentor asks for one.

### 6.4 Evaluation
- 30 hand-labelled papers (`evaluation/papers/labels.jsonl`), labelling budgeted at about 8 hours in weeks 6-7.
- Field-level precision, recall and F1 by field; exact match where meaningful.
- Entity extraction: LLM vs scispaCy precision and recall on the same spans.
- 50 question-answer pairs judged by hand for citation correctness (does the cited passage support the claim?).
- Cost and time per document, per model.
- Failure rate and share of documents needing manual correction.

Human-checked labels only. No LLM self-grading as the headline number.

### 6.5 Deliverable
A Streamlit app where a user uploads a paper, sees the extracted record with page references, searches the collection, asks a question and inspects the evidence. A written evaluation report with the numbers above. Mentor review notes.

---

## 7. Track C: one professional-grade genomics pipeline

### 7.1 Purpose
Show that a bioinformatics workflow can be built to engineering standard: reproducible, containerised, tested in CI, with provenance and a documented comparison against a public reference. This is the pipeline Track A runs for each submission.

### 7.2 Scope
Variant QC and annotation on a bounded public dataset:
- Validate VCF format and sample metadata.
- QC statistics (bcftools stats or equivalent).
- Filtering rules from a versioned config.
- Annotation through a documented public resource (Ensembl VEP REST with caching and rate limiting, or `bcftools csq` with a GFF).
- Summary tables and an HTML report.
- Provenance manifest: tool versions, parameters, input hashes, accession, retrieval date.

### 7.3 Dataset candidates (decided in week 9 with an ADR)
- 1000 Genomes phase 3 open VCF, restricted to one region or a small gene panel.
- Genome in a Bottle HG001 high-confidence calls, restricted the same way.
- Arabidopsis 1001 Genomes VCF if a non-human dataset is preferable.

Criteria: fully open access, documented, small enough for a CI fixture, annotatable with Ensembl resources.

**Safety boundary:** research and educational prototype. No diagnosis, no treatment suggestion, no clinical claim, no controlled-access data.

### 7.4 Evaluation
- Reproducibility: same inputs and environment give identical outputs (hash comparison in CI).
- Annotation coverage and agreement with Ensembl's published consequences for a documented variant set.
- Runtime and memory for the fixture and for the full bounded dataset.
- Completeness of provenance manifest and report.

---

## 8. Track A: genomics service-provider workflow platform

### 8.1 Illustrative business problem
A small sequencing or bioinformatics service receives client variant files and sample metadata, checks completeness and validity, runs QC and an analysis pipeline, drafts a report and delivers it after review. Manual intake, inconsistent metadata, repeated checks and report preparation cause delays and errors.

This process is an **illustrative hypothesis** until a knowledgeable person validates it. Week 13 includes the task of finding one such person (a WUR group, a sequencing service, a former colleague). If none is found by week 16 the process stays labelled illustrative.

### 8.2 Reusable components
1. **Intake and validation**: upload, file-type and schema checks, required fields, missing, duplicated, malformed and out-of-range detection, metadata standardisation, QC summaries, exception reports, versioned validation rules.
2. **Document services** (Track B): used in week 20 for the provider's own SOPs and client request documents.
3. **Pipeline execution** (Track C): worker runs Snakemake per submission, captures logs, handles failure and retry.
4. **Workflow and review**: submission state machine, exception queue, approval gates, audit trail, dashboard.

### 8.3 End-to-end workflow

```text
Submit files + metadata
  -> intake and metadata validation   -> errors -> exception queue
  -> QC checks                        -> QC failure -> review / resubmission
  -> pipeline execution (Track C)     -> pipeline failure -> retry / exception
  -> result processing
  -> draft report
  -> human review: approve / reject with comments
  -> final report package + full audit trail
```

States: `SUBMITTED, VALIDATED, VALIDATION_FAILED, QC_PASSED, QC_FAILED, RUNNING, ANALYSED, PIPELINE_FAILED, DRAFT_REPORT, APPROVED, REJECTED`.

### 8.4 Demonstration features
Submission form, metadata template and versioned schema, synthetic sample sets (valid, incomplete, invalid), QC and exception dashboard, execution status and logs, result and annotation tables, draft report, approve or reject with comments, downloadable final package, audit trail with inputs, actions, status changes and timestamps.

### 8.5 Business value and measurement
Month 5 defines a **simulated manual baseline** (documented assumptions: minutes per manual check, error rates from planted errors) and measures the automated workflow on a synthetic batch of about 200 submissions:
- Validation pass rate, errors caught, false positives.
- Processing and report time per submission.
- Manual intervention rate.
- Rework rate.
- Reviewer time per report.

Label the baseline as simulated everywhere. Do not invent savings.

### 8.6 Food and ingredient adaptation (month 6)
Synthetic supplier specifications and certificates of analysis as PDFs, extracted through Track B, then unit conversion, a reviewable material-name mapping table, specification-limit comparison, exception flags, dashboard and traceable report. Reuses intake, validation, approval and audit components. Tests for unit conversion and specification-limit logic. This is the demonstration that the platform is not hard-coded for genomics, and it connects to the FrieslandCampina experience.

---

# PART II. ROADMAP

## 9. Core roadmap (26 weeks)

### Month 1. Foundation and submission-intake MVP (first slice of Track A)

**Week 1. Requirements and setup**
- Mentor conversation (section 3).
- Track A discovery spec in `docs/architecture/track-a-spec.md`: persona (lab manager at a small sequencing service), illustrative current process, proposed process, inputs (sample manifest CSV plus metadata), outputs, exception cases, approval points, KPIs, simulated baseline definition. Labelled illustrative.
- Repository, README, `docs/decisions/0001-programme-shape.md`, issue list.
- Five synthetic sample-manifest fixtures: valid, missing columns, invalid values, empty, unsupported type.

**Week 2. Python foundation**
- `pyproject.toml`, virtual environment, ruff, mypy, pytest.
- FastAPI app, Pydantic models, health endpoint, config loader, `.env.example`.
- **GitHub Actions CI green.**

**Week 3. Database, upload, validation**
- Postgres in Docker Compose, SQLAlchemy models for submissions and validation results, Alembic migration.
- Safe file upload, schema and required-field validation with versioned rules, stored results.
- Tests for all five fixtures.

**Week 4. First UI and report**
- Streamlit: upload, validation errors, stored records, downloadable validation report.
- Demo GIF, README update. **Evidence package 1, tag v0.1.**

Acceptance: a user uploads a manifest, sees clear errors or stored records, downloads a report; tests cover validation; CI passes; runs locally from the README.

### Month 2. Track B document intelligence v1

**Week 5. PDF ingestion**
- Download script for the 40-50 CC-BY papers with checksums.
- PyMuPDF text and page metadata stored per page. Scanned PDFs: documented limitation.

**Week 6. Typed extraction**
- Pydantic schema for a scientific paper with `unknown` values and source page per field.
- `LLMClient` with structured outputs, response cache, cost log, budget cap, prompt versioning.
- Start hand-labelling 30 papers.

**Week 7. Entity extraction and measurement**
- Finish labels. Field-level precision, recall and F1 script, results in `docs/evaluation/`.
- Entity extraction: LLM vs scispaCy baseline, spans with page and offset.
- Opus 5.5 vs Haiku 5.5 on the labelled set; record cost and accuracy.

**Week 8. Search, grounded Q&A, review**
- PostgreSQL full-text search; Q&A with document and page citations; 50 hand-judged Q&A pairs.
- Streamlit pages: search, ask, inspect evidence, export.
- **Mentor review 1.** **Evidence package 2, tag v0.2.**

### Month 3. Track C pipeline

**Week 9. Dataset and tooling decision**
- Verify candidate datasets (format, metadata, access terms, size). ADR for dataset and for Snakemake vs Nextflow.
- Download script with checksums; accession, version and retrieval date recorded.

**Week 10. Pipeline**
- Snakemake rules: validate VCF, QC stats, filter from config, annotate, summarise.
- Conda or container environment per rule. Tiny fixture VCF runs in CI (dry-run plus real run on the fixture).

**Week 11. Report and provenance**
- HTML report (Jinja), provenance manifest, per-rule tests.

**Week 12. Reference comparison**
- Annotate a documented variant set; coverage and agreement with Ensembl consequences in `docs/evaluation/`.
- Runtime and memory recorded. Limitations and research-only labelling. **Evidence package 3, tag v0.3.**

### Month 4. Track A platform core (main deliverable)

**Week 13. State machine and audit**
- Submission state machine, exception queue, audit-trail table, versioned metadata schema.
- Start looking for a process validator.

**Week 14. Worker**
- Background worker runs the Snakemake pipeline per submission, captures logs, handles failure and retry; execution status in the dashboard.

**Week 15. Report and approval**
- Draft report from pipeline outputs; approve or reject with comments; final package download; provenance chain from upload to report.

**Week 16. End-to-end**
- Synthetic batch demo. Tests: success, invalid submission, QC failure, pipeline failure, rejection.
- App Docker image. **Evidence package 4, tag v0.4.**

### Month 5. Data science and evaluation layer

**Week 17. KPIs vs simulated baseline**
- Synthetic batch of about 200 submissions with planted errors. KPI script and dashboard (Plotly or Power BI). Baseline assumptions documented.

**Week 18. Document classification comparison**
- Document-type or topic classification: TF-IDF plus logistic regression vs LLM, cross-validation, confusion matrix, calibration. Expand the labelled set if time allows.

**Week 19. One justified analytical question**
- Example: predicting QC failure from submission metadata, or variant-burden summaries by group. Proper train and test separation, no leakage, limitations note.

**Week 20. Track B inside Track A**
- Provider SOPs and client request documents through extraction; reports link to cited papers. **Evidence package 5, tag v0.5.**

### Month 6. Adaptation, hardening, deployment, portfolio

**Weeks 21-22. Food and ingredient adaptation** (section 8.6).

**Week 23. Hardening**
- Fixed benchmark inputs, full KPI run, failure-case catalogue, reliability fixes, coverage report.

**Week 24. Deployment**
- One public demo on Streamlit Community Cloud or a Hugging Face Space with a free Postgres. Secrets review, logging, data-retention note.

**Week 25. Documentation**
- Architecture diagrams, three case studies, evaluation report, demo videos, dataset attributions.

**Week 26. Portfolio and career packaging**
- GitHub polish, portfolio page, CV bullets and LinkedIn write-up (outcome on every bullet, only measured claims, and the words "synthetic", "demo" or "mock" never appear in CV text), interview explanation notes per component, **mentor review 2**, gap list. **Evidence package 6, tag v1.0.**

## 10. Optional months 7-9 (in this order, only if no job has started)

1. Second pipeline: RNA-seq differential expression (DESeq2 in Snakemake), plugged into Track A as a second service.
2. Microbiome or proteomics adaptation on processed abundance tables.
3. pgvector semantic search and document comparison.
4. Clementine-specific extension agreed with the mentor (their document types or language).
5. n8n notification integration and basic monitoring.
6. Multi-omics integration only if a compatible public study exists.

## 11. Weekly time allocation

| Activity | Hours |
|---|---:|
| Development | 10 |
| Targeted learning | 4 |
| Testing and debugging | 2 |
| Documentation, GitHub, evidence | 2 |
| Use-case research and mentor contact | 2 |
| **Total** | **20** |

If a feature overruns, cut optional scope (section 17). Never cut tests, provenance, evaluation or the monthly evidence package.

---

# PART III. PROMPT PACK FOR CLAUDE CODE

## 12. How to use this document with Claude Code

1. This file lives at the repository root as `PROJECT_PLAN.md`.
2. Open the repository in Claude Code and paste the Master Project Instruction once per session, or keep it in `CLAUDE.md`.
3. Work one phase, and inside a phase one small task, at a time.
4. Review the proposed design before allowing broad changes. Inspect the diff and run the tests after each change.
5. Keep `PROJECT_PLAN.md`, `README.md`, `CHANGELOG.md` and `docs/decisions/` current.
6. Never ask for a whole month in one prompt.
7. Operating model (added 2026-11-13): `PROGRESS.md` carries the state between sessions; `prompts/phase-N.md` holds one paste-ready block per task; `prompts/session-start.md` and `prompts/session-end.md` open and close every session; `prompts/plan-phase.md` expands a phase into task blocks at its start. One task per session, Sonnet 5.5 by default, Opus 5.5 where a task block says so, no subagents. The phase prompts below remain the reference text.

### 12.1 Master Project Instruction (also the content of `CLAUDE.md`)

```text
You are my senior software engineer, data engineer and technical mentor for this repository.

Read PROJECT_PLAN.md fully before making changes. It defines goals, scope, architecture, roadmap, constraints and acceptance criteria for this portfolio programme.

Help me implement the plan incrementally with maintainable, tested code. Never attempt more than one phase, and inside a phase one small task, at a time.

Working rules:
1. Inspect the existing repository first. Do not assume it is empty.
2. Summarise what exists, identify gaps against PROJECT_PLAN.md, and propose the smallest sensible next step.
3. Before substantial implementation, explain the design, files to change, dependencies to add and trade-offs. Wait for my approval when the change is architectural, destructive, security-sensitive or widens scope.
4. Build one end-to-end vertical slice at a time.
5. Use clear typing, Pydantic models where appropriate, small functions, readable names.
6. Add or update tests for every meaningful feature. Run them and report the real result. Never claim tests passed if they were not run.
7. Handle invalid input, missing data, external-service failure and uncertain AI output explicitly.
8. Secrets live in environment variables. Maintain .env.example. Never hard-code keys.
9. Never put confidential, personal, client or restricted data in code, prompts, logs or fixtures. Synthetic or public data only unless I explicitly confirm otherwise.
10. Preserve provenance and source references for scientific and AI-generated outputs. Never invent citations or silently fill missing values.
11. Nothing here is clinical decision support. No diagnoses, no treatment recommendations.
12. Do not add a dependency without saying why. Prefer simple code over abstraction.
13. All Claude API calls go through the LLMClient interface with caching, cost logging and the monthly budget cap. Model ids come from config.
14. Keep CI green. A task is not done while CI fails.
15. Update documentation and decision records as the project evolves. One ADR per architectural choice.
16. Explain important concepts and decisions as you work. I must be able to discuss this project in technical interviews.
17. If requirements are ambiguous, ask only the single most important question. Do not invent business requirements.
18. At the end of each task report: what was implemented, files changed, dependencies added and why, tests run and their actual results, how I can verify it, known limitations, and the next smallest task.

Start by inspecting the repository and proposing the next step. Do not write application code before reporting findings.
```

### 12.2 Phase 0: repository and environment setup (week 1-2)

```text
Using PROJECT_PLAN.md as the source of truth, initialise this project.

Inspect the repository first. Then propose and, after my approval, create:
- the monorepo layout from section 5.3 (only the directories the first slice needs),
- pyproject.toml with ruff, mypy and pytest configured,
- .gitignore and .env.example,
- a GitHub Actions workflow running ruff, mypy and pytest,
- a FastAPI app with a health endpoint and one passing test,
- CHANGELOG.md and docs/decisions/0002-python-tooling.md.

Do not introduce PostgreSQL, Docker, the Claude API or Snakemake yet. Explain each decision before implementation.
```

### 12.3 Phase 1: submission-intake MVP (weeks 3-4)

```text
Implement the Month 1 MVP in PROJECT_PLAN.md: the first slice of the Track A service-provider workflow.

Input: a synthetic sample-manifest CSV with metadata. Build the full path:
upload -> file checks -> schema and required-field validation with versioned rules -> stored submission and validation results in PostgreSQL (Docker Compose) -> Streamlit screen -> downloadable validation report.

Before coding, propose the manifest schema, validation rules, data models, API endpoints and the minimal UI. Add tests for the five fixtures: valid, missing columns, invalid values, empty, unsupported type. Keep CI green. Do not add features beyond this MVP without asking.
```

### 12.4 Phase 2: document intelligence (weeks 5-8)

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

### 12.5 Phase 3: genomics pipeline (weeks 9-12)

```text
Implement Track C in PROJECT_PLAN.md.

First verify the candidate datasets in section 7.3 (format, metadata, access terms, size) and recommend one with reasons; write the ADR. Recommend Snakemake unless there is a concrete reason for Nextflow; write that ADR too.

Then build the pipeline: VCF validation, QC statistics, config-driven filtering, annotation through a documented Ensembl resource with caching and rate limiting, summary tables, HTML report, provenance manifest (tool versions, parameters, input hashes, accession, retrieval date). Per-rule environments. A tiny fixture must run in GitHub Actions.

Finish with the reference comparison: coverage and agreement with Ensembl's published consequences for a documented variant set, runtime and memory, limitations. Research and educational labelling everywhere. No controlled-access data, no clinical claims.
```

### 12.6 Phase 4: workflow platform core (weeks 13-16)

```text
Implement the Track A platform core in PROJECT_PLAN.md using the intake, validation and pipeline components that already exist.

Build: submission state machine with the states in section 8.3, exception queue, audit-trail table, versioned metadata schema, background worker that runs the Snakemake pipeline per submission with log capture, failure handling and retry, draft report from pipeline outputs, approve/reject with comments, final package download, provenance chain from upload to report, dashboard for status and exceptions.

Add tests for success, invalid submission, QC failure, pipeline failure, rejection. Build the app Docker image. Keep business logic in tested Python modules.
```

### 12.7 Phase 5: data science layer (weeks 17-20)

```text
Implement the month 5 data science layer in PROJECT_PLAN.md.

1. Generate a synthetic batch of about 200 submissions with planted errors; define and document the simulated manual baseline; compute the KPIs in section 8.5; build the dashboard.
2. Document classification: TF-IDF + logistic regression vs the LLM, with cross-validation, confusion matrix and calibration on the labelled set.
3. One justified analytical question with proper train/test separation and a limitations note.
4. Route the provider's SOPs and client request documents through Track B extraction and link reports to cited papers.

Report measured results only. Label the baseline as simulated. Do not claim business savings.
```

### 12.8 Phase 6: food and ingredient adaptation (weeks 21-22)

```text
Adapt the platform to the food and ingredient case in section 8.6 of PROJECT_PLAN.md.

Create synthetic supplier specifications and certificates of analysis as PDFs. Reuse Track B extraction, Track A intake, validation, approval and audit. Add unit conversion, a reviewable material-name mapping table, specification-limit comparison, exception flags, a dashboard and a traceable report. Add tests for unit conversion and specification-limit logic. Do not copy the genomics implementation; show configurability through schemas and processing modules.
```

### 12.9 Phase 7: hardening and deployment (weeks 23-24)

```text
Prepare the project for a public demonstration.

Create fixed benchmark inputs, run the full test suite and KPI scripts, and report measured results only. Review correctness and coverage, provenance, secrets, error handling and logging, dependency risks, reproducibility, setup instructions, performance on representative inputs. Catalogue failure cases.

Then propose and implement the smallest safe deployment: Streamlit Community Cloud or a Hugging Face Space with a free hosted Postgres. No confidential data, no private endpoints exposed. Document known limitations.
```

### 12.10 Phase 8: portfolio packaging (weeks 25-26)

```text
Turn the completed work into an honest technical portfolio.

Prepare README files, architecture diagrams, setup and demo instructions, data-source acknowledgements, evaluation summaries, known limitations, three case studies, demo-video scripts and CV bullet points.

Distinguish completed from planned functionality and synthetic or public-data demonstrations from real approved work. Claim nothing the repository does not evidence. CV bullets state what was built, with what, and what was measured; the words synthetic, demo and mock do not appear in CV text.
```

### 12.11 Optional phases (months 7-9)
Use the Phase 3 prompt as a template for the RNA-seq pipeline, the Phase 6 prompt for the microbiome or proteomics adaptation, and the Phase 2 prompt for pgvector search and document comparison. Agree the Clementine-specific extension with the mentor before writing its prompt.

---

# PART IV. QUALITY, EVALUATION AND PORTFOLIO

## 13. Evaluation framework

| Track | Metric | Shows |
|---|---|---|
| B | Field-level precision, recall, F1, exact match | Extraction reliability |
| B | Entity extraction LLM vs scispaCy | Whether the LLM earns its cost |
| B | Citation correctness on 50 Q&A pairs | Whether answers are supported by sources |
| B | Cost and time per document per model | Operational cost |
| B | Classification accuracy, macro F1, calibration | Whether a cheap baseline suffices |
| C | Byte-identical reruns in CI | Reproducibility |
| C | Annotation coverage and agreement with reference | Pipeline correctness |
| C | Runtime and memory | Operational performance |
| A | Validation pass rate, errors caught, false positives | Whether validation catches real problems without noise |
| A | Processing and report time, manual intervention rate, rework rate | Whether automation reduces work, against a simulated baseline |
| A | Workflow completion rate | Whether submissions pass through the process |

For every metric document test-set size, data source, method, assumptions and limitations.

## 14. Testing strategy
- Unit: validation rules, schema checks, unit conversion, parsing, report generation, state transitions.
- Integration: API with database, file storage, worker.
- Workflow: successful and failing end-to-end paths.
- Pipeline: Snakemake fixture run in CI with output hash check.
- Regression fixtures: fixed synthetic and public examples.
- AI evaluation: hand-labelled extraction set and citation judgements, re-run on every prompt or model change.

A passing suite does not prove scientific validity; method review and reference comparisons are still required.

## 15. Security, privacy and responsible use
- Secrets in environment variables only; `.env` never committed.
- No confidential or client documents to any third-party LLM without explicit authorisation and a data-protection review.
- Synthetic or public data in all public demos. Respect licences, repository terms and consent restrictions.
- Minimise stored personal data; never log document contents or credentials.
- Audit trail for workflow actions and approvals.
- No clinical, diagnostic or treatment claims. Human review mandatory for uncertain extraction and report release.
- AI-generated content marked and traceable to its evidence.

## 16. Portfolio packaging
Three case studies:
1. **Scientific document intelligence**: problem and user, corpus, architecture, example extraction with page references, Q&A with citations, measured evaluation, limitations, mentor feedback.
2. **Genomics pipeline and service workflow**: dataset, pipeline, CI and provenance, reference comparison, the end-to-end submission-to-approval demo, audit trail.
3. **Reuse across genomics and food**: the same platform configured for two domains, KPI results against the simulated baseline, human approval and traceability.

Evidence checklist: public repo, green CI, README and setup, architecture diagram, download scripts or synthetic data, test results, evaluation report, demo video, known limitations, data attributions, no secrets, six monthly evidence packages.

## 17. Scope control

**Must-have (months 1-6):** intake MVP; Track B with measured extraction, search and cited Q&A; Track C pipeline in CI with reference comparison; Track A end-to-end with approval and audit; KPI report against a simulated baseline; food adaptation; one deployed demo; tests, documentation, case studies.

**Cut order when behind (first cut first):** food adaptation (weeks 21-22) → the week 19 analytical question → deployment → entity-extraction baseline comparison → Power BI dashboard (keep Plotly).

**Never cut:** tests, provenance, evaluation sets, the monthly evidence package, honest documentation.

**Optional (months 7-9):** section 10.

**Deferred indefinitely:** every omics modality beyond the above, deep-learning training, autonomous agents, multi-tenant auth and billing, Kubernetes, clinical variant interpretation, a polished commercial frontend.

## 18. First seven days

| Day | Do |
|---|---|
| 1 | `git init`, first commit of this folder, create the GitHub repository, open in Claude Code, paste the Master Project Instruction, run Phase 0 |
| 2 | Mentor conversation booked or held; Track A discovery spec drafted |
| 3 | Five manifest fixtures written; validation rules written down in the spec |
| 4 | Python tooling, FastAPI health endpoint, first test, CI green |
| 5 | Issue list for weeks 3-4 in GitHub Issues |
| 6 | Begin Phase 1: Postgres via Docker Compose, data models |
| 7 | Review the week: what was learned, what the next smallest task is, `docs/evidence/week-1.md` |

## 19. Status tracker

| Workstream | Status | Next milestone |
|---|---|---|
| Programme setup | Plan written 2026-11-12; git initialised and prompt kit added 2026-11-13 | GitHub remote, Phase 0 task 0.1 |
| Mentor agreement | Not started | Week 1 conversation, notes in docs/evidence |
| Intake MVP (Track A slice 1) | Not started | v0.1 end of week 4 |
| Document intelligence (Track B) | Not started | v0.2 end of week 8, mentor review 1 |
| Genomics pipeline (Track C) | Not started | v0.3 end of week 12 |
| Platform core (Track A) | Not started | v0.4 end of week 16 |
| Data science layer | Not started | v0.5 end of week 20 |
| Food adaptation | Not started | Weeks 21-22 |
| Hardening and deployment | Not started | Week 24 |
| Portfolio | Not started | v1.0 end of week 26, mentor review 2 |

## 20. Resources
- Python https://docs.python.org/3/ , FastAPI https://fastapi.tiangolo.com/ , Pydantic https://docs.pydantic.dev/ , SQLAlchemy https://docs.sqlalchemy.org/ , PostgreSQL https://www.postgresql.org/docs/ , Streamlit https://docs.streamlit.io/ , pytest https://docs.pytest.org/ , Snakemake https://snakemake.readthedocs.io/ , Docker https://docs.docker.com/ , GitHub Actions https://docs.github.com/actions
- Anthropic SDK and API docs https://platform.claude.com/docs/ , scispaCy https://allenai.github.io/scispacy/ , PyMuPDF https://pymupdf.readthedocs.io/
- PMC Open Access subset https://www.ncbi.nlm.nih.gov/pmc/tools/openftlist/ , Ensembl https://www.ensembl.org/ , Ensembl VEP REST https://rest.ensembl.org/ , 1000 Genomes https://www.internationalgenome.org/ , Genome in a Bottle https://www.nist.gov/programs-projects/genome-bottle , 1001 Genomes https://1001genomes.org/ , bcftools https://samtools.github.io/bcftools/

Check licences, rate limits and attribution requirements before use. Record versions and retrieval dates.

## 21. Definition of success
After six months the developer can demonstrate and explain, with evidence in the repository:
1. A typed Python application and API with CI, containers and migrations.
2. Ingestion, validation, storage and provenance for structured and unstructured data.
3. A document extraction and retrieval workflow with measured evidence quality and a mentor's review.
4. A reproducible bioinformatics pipeline built to engineering standard.
5. A business workflow with validation, QC, pipeline execution, reporting and human approval, measured against a documented baseline.
6. Honest evaluation and communication of limitations.
7. Effective use of AI coding tools while owning and understanding the implementation.
