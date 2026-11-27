# ADR 0007: Validation on upload and the read API

- Status: accepted
- Date: 2026-11-27
- Task: 1.4

## Context

Uploading (ADR 0005) and validating (ADR 0006) existed separately. They now have to be joined so that every issue is stored with its rule set version, a failure in validation never marks a file valid or loses it (spec section 6), and clients can read the results.

## Decisions

**Validation runs inside the upload request.** A manifest has at most 1,000 rows, so the check is quick. A queue and a worker would add moving parts that Phase 1 does not need.

**Two transactions.** Intake commits the row as `SUBMITTED`. Validation then stores the issues, the status and `rule_set_version` in a second transaction. If anything in the second fails (engine, reading the file, saving results), it rolls back as a whole, so there are never partial results.

**A validation failure of our own is not an HTTP error.** The response is 201 with status `SUBMITTED`. The submission exists, and a 5xx would invite a retry that gets 409. The log holds the submission id, the exception class and the stack frames, but not the exception message, which can quote client data.

**201 means accepted, not valid.** A file with errors is a recorded submission with status `VALIDATION_FAILED`. Warnings never block.

**The validation date is today in UTC**, supplied by a FastAPI dependency, so tests fix it.

**Issues are not capped; the input is.** The header is limited to 50 columns (`TOO_MANY_COLUMNS`) and the rows to `MAX_MANIFEST_ROWS`, which bounds the issues at roughly 10,000 with the defaults. Truncating stored issues was rejected: a client must see everything there is to fix. The column limit is a file rule (spec section 7), like the row limit, so the rule set stays `v1`; no release had used `v1` yet.

**Read API.** `GET /submissions` is paginated with `limit` (1 to 100, default 20) and `offset`, newest first with the id as tie-breaker. It leaves out metadata, so contact emails are not returned in bulk. `GET /submissions/{id}` returns the metadata and all issues. There are no update or delete endpoints: a correction is a new submission.

## Trade-offs and known limitations

- A submission left at `SUBMITTED` cannot be validated again: there is no endpoint for it, and uploading the same bytes gives 409. Staff action comes with the exception queue in Phase 4.
- If the process dies between the two transactions, the submission stays `SUBMITTED` and nothing is logged.
- The validation date is not stored. For a validated submission it is the date of `updated_at`, except possibly for an upload right at midnight UTC.
- A client ahead of UTC can have a same-day `collection_date` rejected as future in the first hours of their day.
- Offset pagination can repeat or skip an item when uploads arrive between two page requests.
- Issues in the detail response are not paginated.
- Without authentication, anyone who can reach the API can read every submission, including contact emails. Acceptable only while all data is synthetic.

## Dependencies added

None.

## Not decided here

Background processing, re-validation, filtering the list, authentication.
