"""Check a manifest file against a rule set.

Order (spec section 9): file level, then header, then rows. A file-level problem stops the
checks and is the only issue returned; a header problem does not stop them.

The engine reads one file and returns issues. It has no database, API, settings or clock:
the caller passes the validation date, so a result can be reproduced later. A file that
cannot be opened raises OSError, because that is not a fault in the client's data.
"""

import csv
import io
import re
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import assert_never

from lifesciences_platform.common.validation.models import (
    MAX_COLUMN_NAME_LENGTH,
    IssueCode,
    Severity,
    ValidationIssue,
)
from lifesciences_platform.common.validation.rules import (
    ColumnRule,
    DateColumn,
    DecimalColumn,
    EnumColumn,
    RuleSet,
    TextColumn,
)

DEFAULT_MAX_MANIFEST_ROWS = 1000  # track-a-spec.md section 7
# Spec section 7. Without a limit, a header of mostly commas would give one warning per
# comma: millions of issues from a file within the upload size limit.
MAX_HEADER_COLUMNS = 50
MAX_SHOWN_VALUE_LENGTH = 60

# Checked before conversion: Decimal() also accepts "nan", "inf", "1e2" and "1_000",
# and date.fromisoformat() also accepts "20260914".
DECIMAL_FORMAT = re.compile(r"[+-]?([0-9]+(\.[0-9]*)?|\.[0-9]+)")
DATE_FORMAT = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}")


@dataclass(frozen=True)
class _Record:
    line: int  # line on which the record starts; a quoted cell may span several
    cells: list[str]  # already trimmed


class _FileError(Exception):
    """The file cannot be checked any further."""

    def __init__(self, code: IssueCode, message: str) -> None:
        super().__init__(message)
        self.issue = _issue(code, message)


def validate_manifest(
    path: Path,
    rule_set: RuleSet,
    *,
    today: date,
    max_rows: int = DEFAULT_MAX_MANIFEST_ROWS,
) -> list[ValidationIssue]:
    """Return every issue in the manifest. An empty list means no errors and no warnings."""
    try:
        header, rows = _read_table(path, max_rows)
    except _FileError as error:
        return [error.issue]
    return _check_header(header, rule_set) + _check_rows(header, rows, rule_set, today)


# ------------------------------------------------------------------ file level


def _read_table(path: Path, max_rows: int) -> tuple[list[str], list[_Record]]:
    if not path.name.lower().endswith(".csv"):
        raise _FileError(IssueCode.UNSUPPORTED_FILE_TYPE, "Only .csv files can be validated.")

    records = _parse(_decode(path.read_bytes()))
    if not records:
        raise _FileError(IssueCode.EMPTY_FILE, "The file contains no values.")
    header, rows = records[0].cells, records[1:]
    if len(header) > MAX_HEADER_COLUMNS:
        raise _FileError(
            IssueCode.TOO_MANY_COLUMNS,
            f"The header has {len(header)} columns; the limit is {MAX_HEADER_COLUMNS}.",
        )

    for record in rows:
        if len(record.cells) != len(header):
            raise _FileError(
                IssueCode.MALFORMED_CSV,
                f"Line {record.line} has {len(record.cells)} fields but the header has "
                f"{len(header)}. Fields must be separated by commas.",
            )
    _refuse_repeated_names(header)

    if not rows:
        raise _FileError(IssueCode.NO_DATA_ROWS, "The file has a header but no data rows.")
    if len(rows) > max_rows:
        raise _FileError(
            IssueCode.TOO_MANY_ROWS,
            f"The file has {len(rows)} data rows; the limit is {max_rows}.",
        )
    return header, rows


def _decode(content: bytes) -> str:
    if not content:
        raise _FileError(IssueCode.EMPTY_FILE, "The file is empty (0 bytes).")
    try:
        text = content.decode("utf-8-sig")  # drops the byte-order mark Excel adds
    except UnicodeDecodeError as error:
        raise _FileError(IssueCode.MALFORMED_CSV, "The file is not valid UTF-8 text.") from error
    if "\x00" in text:
        raise _FileError(IssueCode.MALFORMED_CSV, "The file contains NUL bytes; it is not text.")
    return text


def _parse(text: str) -> list[_Record]:
    """Split into records, trimming cells and dropping records in which every cell is empty."""
    # strict=True: without it an unclosed quote silently swallows the rest of the file.
    reader = csv.reader(io.StringIO(text, newline=""), strict=True)
    records: list[_Record] = []
    start_line = 1
    try:
        for raw_cells in reader:
            cells = [cell.strip() for cell in raw_cells]
            if any(cells):
                records.append(_Record(start_line, cells))
            start_line = reader.line_num + 1
    except csv.Error as error:
        raise _FileError(
            IssueCode.MALFORMED_CSV,
            f"The CSV cannot be read: the record starting on line {start_line} is broken "
            f"({error}).",
        ) from error
    return records


def _refuse_repeated_names(header: list[str]) -> None:
    """With two columns of one name, one of them would be silently ignored."""
    seen: set[str] = set()
    for name in header:
        if name and name in seen:
            raise _FileError(
                IssueCode.MALFORMED_CSV,
                f"The column name {_shown(name)} appears more than once in the header.",
            )
        seen.add(name)


# ------------------------------------------------------------------ header level


def _check_header(header: list[str], rule_set: RuleSet) -> list[ValidationIssue]:
    present = set(header)
    known = {rule.name for rule in rule_set.columns}
    issues = [
        _issue(
            IssueCode.MISSING_COLUMN,
            f"The required column {rule.name!r} is not in the header.",
            column=rule.name,
        )
        for rule in rule_set.columns
        if rule.required and rule.name not in present
    ]
    for position, name in enumerate(header, start=1):
        if name in known:
            continue
        described = f"Column {_shown(name)}" if name else f"Column {position}, which has no name,"
        issues.append(
            _issue(
                IssueCode.UNKNOWN_COLUMN,
                f"{described} is not part of the manifest and is ignored.",
                column=_safe_column_name(name),
            )
        )
    return issues


# ------------------------------------------------------------------ rows


def _check_rows(
    header: list[str], rows: list[_Record], rule_set: RuleSet, today: date
) -> list[ValidationIssue]:
    positions = {name: index for index, name in enumerate(header)}
    first_seen: dict[str, int] = {}  # unique column value -> line it first appeared on
    issues: list[ValidationIssue] = []

    for record in rows:
        valid: dict[str, str] = {}  # only values that passed their own column's rule
        for rule in rule_set.columns:
            if rule.name not in positions:
                continue  # reported once, as MISSING_COLUMN
            value = record.cells[positions[rule.name]]
            if not value:
                if rule.required:
                    issues.append(
                        _issue(
                            IssueCode.MISSING_VALUE,
                            f"{rule.name} is required but the cell is empty.",
                            row=record.line,
                            column=rule.name,
                        )
                    )
                continue

            problem = _check_value(rule, value, today)
            if problem is not None:
                code, expected = problem
                issues.append(
                    _issue(
                        code,
                        f"{rule.name}: found {_shown(value)}, expected {expected}.",
                        row=record.line,
                        column=rule.name,
                    )
                )
                continue
            valid[rule.name] = value

            if rule.name == rule_set.unique_column:
                first_line = first_seen.setdefault(value, record.line)
                if first_line != record.line:
                    issues.append(
                        _issue(
                            IssueCode.DUPLICATE_SAMPLE_ID,
                            f"{rule.name} {_shown(value)} was already used on line {first_line}.",
                            row=record.line,
                            column=rule.name,
                        )
                    )

        issues += _check_dependent_value(valid, rule_set, record.line)
    return issues


def _check_value(rule: ColumnRule, value: str, today: date) -> tuple[IssueCode, str] | None:
    """Return the code and what was expected, or None when the value is acceptable."""
    match rule:
        case TextColumn():
            if value.isprintable() and re.fullmatch(rule.pattern, value):
                return None
            return IssueCode.INVALID_VALUE, rule.expected
        case EnumColumn():
            if value in rule.allowed:
                return None
            return IssueCode.INVALID_VALUE, "one of: " + ", ".join(rule.allowed)
        case DecimalColumn():
            allowed = f"a number from {rule.minimum} to {rule.maximum}"
            if not DECIMAL_FORMAT.fullmatch(value):
                return IssueCode.INVALID_TYPE, f"{allowed}, with '.' as decimal separator"
            if not rule.minimum <= Decimal(value) <= rule.maximum:
                return IssueCode.OUT_OF_RANGE, allowed
            return None
        case DateColumn():
            parsed = _parse_date(value)
            if parsed is None:
                return IssueCode.INVALID_TYPE, "a real date written as YYYY-MM-DD"
            if parsed > today:
                return IssueCode.OUT_OF_RANGE, f"a date not later than {today.isoformat()}"
            return None
        case _:
            assert_never(rule)


def _parse_date(value: str) -> date | None:
    if not DATE_FORMAT.fullmatch(value):
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:  # right shape, impossible date such as 2026-13-01
        return None


def _check_dependent_value(
    valid: dict[str, str], rule_set: RuleSet, line: int
) -> list[ValidationIssue]:
    """Runs only when both cells are individually valid (spec section 8.1)."""
    rule = rule_set.dependent_value
    if rule.column not in valid or rule.depends_on not in valid:
        return []
    source = valid[rule.depends_on]
    required = rule.required_value[source]
    if valid[rule.column] == required:
        return []
    return [
        _issue(
            IssueCode.INCONSISTENT_REFERENCE,
            f"{rule.column} {valid[rule.column]!r} does not match {rule.depends_on} "
            f"{source!r}; expected {required!r}.",
            row=line,
            column=rule.column,
        )
    ]


# ------------------------------------------------------------------ helpers


def _issue(
    code: IssueCode, message: str, *, row: int | None = None, column: str | None = None
) -> ValidationIssue:
    severity = Severity.WARNING if code is IssueCode.UNKNOWN_COLUMN else Severity.ERROR
    return ValidationIssue(severity=severity, code=code, message=message, row=row, column=column)


def _shown(value: str) -> str:
    """Quote client text for a message: shortened, with unprintable characters escaped."""
    if len(value) > MAX_SHOWN_VALUE_LENGTH:
        value = value[:MAX_SHOWN_VALUE_LENGTH] + "..."
    return repr(value)


def _safe_column_name(name: str) -> str | None:
    """A client's column name, made safe to store; None when the header cell is empty."""
    escaped = "".join(c if c.isprintable() else repr(c)[1:-1] for c in name)
    return escaped[:MAX_COLUMN_NAME_LENGTH] or None
