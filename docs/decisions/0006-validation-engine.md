# ADR 0006: Validation engine and rule sets

- Status: accepted
- Date: 2026-11-27
- Task: 1.3

## Context

An uploaded manifest must be checked against the rules in the Track A spec (sections 7 to 9). Every result has to be traceable to a rule set version, a client has to be able to fix a file from the messages alone, and the Phase 1 tests and the Month 5 evaluation both need the same file to give the same issues every time.

## Decisions

**Rules are data, in Python.** `common/validation/rules.py` holds `RULE_SET_V1` as frozen dataclasses: one entry per column, the unique column and the organism to reference genome map. `engine.py` knows the kinds of rule (text pattern, enum, decimal range, date) but no column names. A released rule set is never edited; a change is a new version.

**The engine is pure.** `validate_manifest(path, rule_set, *, today, max_rows)` reads one file and returns issues. It imports no database, API or settings code and never reads the clock. `Severity` moved here from `workflows/models.py`, which re-exports it, so the database depends on the engine's types and not the other way round.

**Problems in the data are return values; problems in the system are exceptions.** A broken file produces issues. A file that cannot be opened raises `OSError`, so a storage fault is never reported to a client as a bad manifest.

**Standard-library `csv`, strict mode.** It keeps every value as the text the client wrote and gives line numbers. Strict mode stops an unclosed quote from swallowing the rest of the file.

**Format before conversion.** Numbers and dates are matched against an explicit pattern first, because `Decimal` accepts `nan`, `inf` and `1e2`, and `date.fromisoformat` accepts `20260901`.

**Client text is untrusted in the output too.** Values quoted in messages are shortened and escaped; column names are escaped and cut to the database column length.

## Choices the spec did not cover (now written into it)

| Case | Result |
|---|---|
| Column name used twice | `MALFORMED_CSV` |
| Header cell with no name | `UNKNOWN_COLUMN` warning, no column name |
| Record in which every cell is empty (such as `,,,,`) | Ignored like a blank line |
| NUL byte | `MALFORMED_CSV` |
| File with no values at all, only commas | `EMPTY_FILE` |
| Unprintable character in a text value | `INVALID_VALUE` |
| Repeated `sample_id` that is itself invalid | `INVALID_VALUE` on each, no `DUPLICATE_SAMPLE_ID` |

## Trade-offs and known limitations

- Changing a rule means changing code. In exchange, mypy checks the rule set and no loader or file format is needed.
- The rule kinds are a closed list; a new kind needs engine code.
- The whole file is read into memory, which the 5 MB upload limit bounds.
- The number of header columns is not limited. A file made mostly of commas in the header could produce a very large number of `UNKNOWN_COLUMN` warnings. Task 1.4 stores issues and should decide on a cap first.
- Messages quote client values. The reports built in task 1.5 must escape them in HTML and guard against spreadsheet formulas in CSV.

## Dependencies added

None.

## Not decided here

Excel input, rule sets editable by users, choosing a rule set per client.
