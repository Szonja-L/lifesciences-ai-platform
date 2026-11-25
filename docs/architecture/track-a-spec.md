# Track A discovery spec: sequencing-service submission intake

> **Illustrative, not validated with a service provider.** This process is a working hypothesis written from public knowledge of how small sequencing services operate. No provider has reviewed it. Plan section 8.1 schedules the search for one reviewer (week 13); if none is found by week 16, this label stays. All data in this project is synthetic.

Status: v1, written 2026-11-25 (task 0.4). Manifest rule set version described here: `v1`.

Nothing in this workflow is clinical decision support. It checks files and metadata; it makes no diagnosis and no treatment recommendation.

## 1. Persona

**Lab manager at a small sequencing and bioinformatics service** (illustrative).

- Runs a team of three to six people that accepts DNA samples or variant files from external clients (academic groups, small biotech companies), runs QC and an analysis pipeline, and returns a report.
- Receives several submissions a week, each with a sample manifest spreadsheet and a few lines of project information in an email or web form.
- Cares about: catching bad metadata before lab or compute time is spent, knowing which submission is stuck where, and showing a client exactly what was wrong with their file.
- Frustrations: manifests arrive in many layouts, the same mistakes recur (missing columns, free-text organism names, duplicated sample ids), and the checks live in one person's head.

## 2. Current process (illustrative)

1. Client emails a manifest (Excel or CSV) and a short description of the project.
2. A staff member opens the file and checks it by eye against an internal checklist.
3. Problems go back to the client by email; the corrected file comes back days later, sometimes with new problems.
4. Once accepted, someone copies the metadata into a spreadsheet or LIMS by hand.
5. QC and the pipeline are started manually; status is tracked in a shared spreadsheet.
6. An analyst drafts the report in a document template; the lab manager reviews and sends it.

Pain points this project addresses: inconsistent metadata, repeated manual checks, no record of which rule version a file was checked against, no audit trail of status changes, and slow report preparation.

## 3. Proposed process

The states are the ones in plan section 8.3. Phase 1 implements only intake and validation (the first two lines).

| Step | What happens | Resulting state |
|---|---|---|
| Submit | Client uploads one manifest CSV plus submission metadata through a form or `POST /submissions`. File type and size are checked at the door. | `SUBMITTED` |
| Validate | The manifest is checked against a versioned rule set (section 9). Every issue is stored with code, severity, row and column. | `VALIDATED` (no errors) or `VALIDATION_FAILED` |
| Exception handling | Failed submissions appear in an exception queue with a downloadable validation report. The client fixes the file and submits again as a new submission. | new `SUBMITTED` |
| QC (later phase) | Per-sample QC checks on the referenced variant files. | `QC_PASSED` / `QC_FAILED` |
| Pipeline (Track C) | Snakemake run per submission, logs captured, retry on failure. | `RUNNING` → `ANALYSED` / `PIPELINE_FAILED` |
| Report | Draft report generated from results. | `DRAFT_REPORT` |
| Review | Lab manager approves or rejects with comments. | `APPROVED` / `REJECTED` |

A validated submission is never edited in place; a correction is a new submission. This keeps every validation result tied to exactly the file it describes (by SHA-256 content hash).

## 4. Inputs

### 4.1 Sample manifest

One CSV file per submission, one row per sample. Schema in section 8, file rules in section 7.

The manifest *references* each sample's variant file by name (`variant_file`). In Phase 1 only the name is checked; the variant files themselves are neither uploaded nor read. They enter in the QC phase.

### 4.2 Submission metadata

Form fields sent with the upload. They describe the submission, not individual samples.

| Field | Type | Required | Rule | Example |
|---|---|---|---|---|
| `client_id` | string | yes | `C-` followed by 3 digits | `C-001` |
| `project_name` | string | yes | 1 to 100 characters | `Synthetic exome batch A` |
| `requested_analysis` | enum | yes | `variant_calling_qc`, `variant_annotation` | `variant_annotation` |
| `contact_email` | string | yes | valid email format; fixtures use `@example.org` only | `lab-contact@example.org` |

Recorded by the system, never entered by the client: submission id, upload time, original filename, content hash, size in bytes, rule set version.

## 5. Outputs

- **Submission record**: metadata, file hash, status, timestamps.
- **Validation result list**: one entry per issue (`severity`, `code`, `message`, `row`, `column`, `rule_set_version`).
- **Validation report** (downloadable): summary counts by code and severity, then the issue list, so the client can fix the file without contacting staff.
- **Audit trail entry** for every status change (from Phase 4; Phase 1 stores the status and the timestamps only).
- Later phases: QC summary, pipeline logs, draft and final report package.

## 6. Exception cases

| Case | Where caught | Outcome |
|---|---|---|
| Wrong file type (not `.csv`, or wrong content type) | Upload | HTTP 4xx, no submission created (`UNSUPPORTED_FILE_TYPE`) |
| File larger than the size limit | Upload | HTTP 413, no submission created (`FILE_TOO_LARGE`) |
| Same file uploaded twice (same content hash) | Upload | HTTP 409, points to the existing submission |
| Empty file, header only, unreadable CSV, too many rows | Validation, file level | `VALIDATION_FAILED`, one file-level issue, row checks skipped |
| Required column missing | Validation, header level | `VALIDATION_FAILED`; present columns are still checked |
| Bad value in a row | Validation, row level | `VALIDATION_FAILED` with row and column of every bad cell |
| Unknown extra column | Validation, header level | Warning only; submission can still be `VALIDATED` |
| Validation engine crashes on unexpected input | Validation | Submission stays `SUBMITTED`, error logged, shown in the exception queue as "needs staff"; never silently marked valid |
| QC or pipeline failure | Later phases | `QC_FAILED` / `PIPELINE_FAILED`, retry or exception queue |

## 7. File rules

| Rule | Value | Code if broken |
|---|---|---|
| Extension | `.csv` only (case-insensitive) | `UNSUPPORTED_FILE_TYPE` |
| Content type | `text/csv` (also accept `application/vnd.ms-excel`, which some browsers send for CSV) | `UNSUPPORTED_FILE_TYPE` |
| Maximum size | 5 MB (a setting, `MAX_UPLOAD_BYTES`) | `FILE_TOO_LARGE` |
| Encoding | UTF-8; a leading UTF-8 byte-order mark is accepted (Excel adds one) | `MALFORMED_CSV` |
| Delimiter | comma | `MALFORMED_CSV` if rows have a different field count from the header |
| Header | first line; column names matched exactly after trimming whitespace; column order is free | see section 9 |
| Data rows | at least 1, at most 1,000 (a setting, `MAX_MANIFEST_ROWS`) | `NO_DATA_ROWS`, `TOO_MANY_ROWS` |
| Blank lines | fully blank lines are ignored, not counted as rows | none |

## 8. Manifest schema (rule set v1)

All values are trimmed of surrounding whitespace before checking. Enum values are case-sensitive. An empty cell counts as missing.

| Column | Type | Required | Allowed values / rule | Example |
|---|---|---|---|---|
| `sample_id` | string | yes | `S-` followed by exactly 4 digits (`^S-\d{4}$`); unique within the file | `S-0001` |
| `client_sample_label` | string | no | 1 to 64 characters; letters, digits, `_` and `-` only | `ctrl_rep1` |
| `organism` | enum | yes | `Homo sapiens`, `Mus musculus` | `Homo sapiens` |
| `reference_genome` | enum | yes | `GRCh38`, `GRCm39`; must match `organism` (section 8.1) | `GRCh38` |
| `sample_type` | enum | yes | `blood`, `saliva`, `tissue`, `cell_line`, `dna_extract` | `blood` |
| `assay` | enum | yes | `WGS`, `WES`, `targeted_panel` | `WES` |
| `variant_file` | string | yes | file name only (no `/` or `\`), ending `.vcf` or `.vcf.gz` | `S-0001.vcf.gz` |
| `dna_conc_ng_per_ul` | decimal | yes | number with `.` as decimal separator; 0.5 to 500 inclusive | `42.5` |
| `collection_date` | date | yes | ISO `YYYY-MM-DD`; a real calendar date; not later than the validation date | `2026-09-14` |

### 8.1 Cross-field rule

| Organism | Required reference genome |
|---|---|
| `Homo sapiens` | `GRCh38` |
| `Mus musculus` | `GRCm39` |

The consistency check runs only when both cells are individually valid. An invalid organism produces one `INVALID_VALUE`, not a second `INCONSISTENT_REFERENCE`.

### 8.2 A valid manifest, in one sentence

A UTF-8 comma-separated `.csv` of at most 5 MB, with a header containing all eight required columns, between 1 and 1,000 data rows, every required cell filled and every cell matching the rules above, unique `sample_id` values, and a reference genome that matches each organism. Unknown extra columns are allowed and produce a warning.

## 9. Validation issues and codes

Each issue has: `severity` (`error` or `warning`), `code` (stable string, never renamed once released), `message` (plain English, says what was found and what is expected), `row` and `column`.

`row` is the **file line number** (header = line 1, so the first data row is row 2), so a user can find it in any editor. `row` is empty for file- and header-level issues; `column` is empty for file-level issues.

A submission is `VALIDATED` when it has zero `error` issues. Warnings never block.

| Code | Severity | Level | Raised when |
|---|---|---|---|
| `UNSUPPORTED_FILE_TYPE` | error | file | Extension or content type not allowed |
| `FILE_TOO_LARGE` | error | file | Size over `MAX_UPLOAD_BYTES` (upload only) |
| `EMPTY_FILE` | error | file | File has 0 bytes, or only whitespace |
| `MALFORMED_CSV` | error | file | Not valid UTF-8, or a row's field count differs from the header's |
| `NO_DATA_ROWS` | error | file | Header present, no data rows |
| `TOO_MANY_ROWS` | error | file | More than `MAX_MANIFEST_ROWS` data rows; row checks skipped |
| `MISSING_COLUMN` | error | header | A required column is absent (one issue per column) |
| `UNKNOWN_COLUMN` | warning | header | A column not in the schema (one issue per column) |
| `MISSING_VALUE` | error | cell | A required cell is empty |
| `INVALID_TYPE` | error | cell | A value cannot be read as its type (not a number, not a real date) |
| `INVALID_VALUE` | error | cell | Wrong pattern, not an allowed enum value, or a disallowed character or extension |
| `OUT_OF_RANGE` | error | cell | A number or date outside its allowed range (including a future date) |
| `DUPLICATE_SAMPLE_ID` | error | cell | A `sample_id` already seen earlier in the file; reported on the later row |
| `INCONSISTENT_REFERENCE` | error | row | `reference_genome` does not match `organism` |

Order of checks: file level → header level → rows. A file-level error stops further checks. A header-level error does not.

## 10. Approval points

| Point | Who | Phase |
|---|---|---|
| Accept or reject a submission that passed validation only with warnings | Lab staff | Phase 4 (Phase 1 accepts automatically) |
| Release a submission from the exception queue after a crash | Lab staff | Phase 4 |
| Approve or reject the draft report, with comments | Lab manager | Report phase |
| Change the validation rule set (new version) | Lab manager, recorded in git and an ADR | Any |

Validation itself is automatic. A human decides everything that leaves the service.

## 11. KPIs

Measured in Month 5 on a synthetic batch of about 200 submissions (plan section 8.5):

- Validation pass rate.
- Planted errors caught (recall) and false positives (issues on cells with no planted error).
- Processing time per submission, upload to final state.
- Report time per submission.
- Manual intervention rate: share of submissions that need a human outside the approval points.
- Rework rate: share of submissions resubmitted at least once.
- Reviewer time per report.

## 12. Simulated manual baseline (definition)

The baseline is **simulated**: it is a model of manual work built from stated assumptions, not a measurement. Every number below is a placeholder to be revised in Month 5 and, ideally, by a service provider. Wherever a comparison is shown, it is labelled "simulated baseline".

| Assumption | Placeholder value | Why it is needed |
|---|---|---|
| Minutes to open and check one manifest by eye, fixed part | 5 | Per-submission handling time |
| Additional minutes per sample row | 0.5 | Scales with batch size |
| Share of planted errors a manual check misses | 10% | Gives manual recall to compare with automated recall |
| Minutes to write one rejection email | 10 | Cost of an exception |
| Minutes to transcribe metadata into a tracking sheet, per row | 0.3 | Cost removed by stored records |

Rules for using the baseline: list the assumptions next to every comparison; show results for a low and a high value of each assumption; never present a saving as observed.

## 13. Fixtures

The five Phase 1 fixtures live in `tests/fixtures/manifests/`; their README lists the exact issues each one must produce. Larger synthetic batches and labelled sets for Month 5 live in `evaluation/`.

## 14. Out of scope for v1

Excel (`.xlsx`) upload, reading variant file contents, multiple manifests per submission, client accounts and authentication, regulatory or accreditation requirements (deliberately not modelled; the process is generic).
