# Sample manifest fixtures (rule set v1)

Five synthetic files for the Phase 1 intake and validation tests. All values are invented: sample ids are `S-` plus digits, labels are placeholders, there are no real people, clients or samples. The schema and codes they test are defined in [`docs/architecture/track-a-spec.md`](../../../docs/architecture/track-a-spec.md), sections 7 to 9.

`row` below is the file line number (header = row 1), as in the spec.

## `valid.csv`

Five rows, all required columns, both organisms, all five `sample_type` values and all three `assay` values. Includes boundary values on purpose: `dna_conc_ng_per_ul` of exactly `0.5` (row 5) and `500` (row 6), an empty optional `client_sample_label` (row 4), and a plain `.vcf` next to `.vcf.gz`.

Expected: **no issues.** Submission becomes `VALIDATED`.

## `missing_columns.csv`

Three otherwise valid rows. The header has no `assay` and no `collection_date` column.

Expected: exactly two issues, both header level, both `error`:

| Code | Column |
|---|---|
| `MISSING_COLUMN` | `assay` |
| `MISSING_COLUMN` | `collection_date` |

No row-level issues (the present columns are all valid). Submission becomes `VALIDATION_FAILED`.

## `invalid_values.csv`

Twelve data rows, each with exactly one planted error, plus one extra column `notes` that is not in the schema.

| Row | Column | Planted value | Expected code |
|---|---|---|---|
| (header) | `notes` | extra column | `UNKNOWN_COLUMN` (warning) |
| 2 | `sample_id` | `S-01` | `INVALID_VALUE` |
| 3 | `organism` | `Homo sapien` | `INVALID_VALUE` (no `INCONSISTENT_REFERENCE`, see spec 8.1) |
| 4 | `assay` | empty | `MISSING_VALUE` |
| 5 | `dna_conc_ng_per_ul` | `abc` | `INVALID_TYPE` |
| 6 | `dna_conc_ng_per_ul` | `900` | `OUT_OF_RANGE` |
| 7 | `collection_date` | `2026-13-01` | `INVALID_TYPE` |
| 8 | `collection_date` | `2099-01-01` | `OUT_OF_RANGE` (future date) |
| 9 | `reference_genome` | `GRCh38` with `Mus musculus` | `INCONSISTENT_REFERENCE` |
| 10 | `variant_file` | `S-0109.bam` | `INVALID_VALUE` |
| 11 | `sample_id` | `S-0102` (already on row 3) | `DUPLICATE_SAMPLE_ID` |
| 12 | `client_sample_label` | `ctrl rep#11` | `INVALID_VALUE` |
| 13 | `sample_type` | `plasma` | `INVALID_VALUE` |

Expected: 12 errors and 1 warning, nothing else. Submission becomes `VALIDATION_FAILED`.

Note for row 8: `2099-01-01` stays in the future until 2099. Tests should still pass "today" into the engine explicitly rather than read the system clock.

## `empty.csv`

Zero bytes.

Expected: one file-level `EMPTY_FILE` error, no other checks run. Submission becomes `VALIDATION_FAILED`.

## `unsupported_type.txt`

Plain text with a `.txt` extension.

Expected: rejected at upload with `UNSUPPORTED_FILE_TYPE` (HTTP 4xx, no submission created). If passed straight to the validation engine, the same code.

## Not covered by a fixture

`FILE_TOO_LARGE`, `MALFORMED_CSV`, `NO_DATA_ROWS`, `TOO_MANY_ROWS` and `TOO_MANY_COLUMNS` are defined in the spec but have no file here; tests generate those inputs in memory (a header-only string, a non-UTF-8 byte string, 1,001 generated rows, a header of commas), which keeps large or binary files out of git.

## Rules for editing

- Keep every value synthetic and obviously so.
- If you change a fixture, update this table in the same commit; the Phase 1 tests assert exactly these codes.
- Files must stay byte-for-byte stable (LF line endings, see `.gitattributes`), because the upload tests compare SHA-256 hashes.
