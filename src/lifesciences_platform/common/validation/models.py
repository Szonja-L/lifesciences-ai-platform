"""Types describing what validation found (spec: docs/architecture/track-a-spec.md section 9)."""

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

# Length of validation_results.column_name in the database.
MAX_COLUMN_NAME_LENGTH = 255


class Severity(StrEnum):
    """Only errors block validation; warnings never do."""

    ERROR = "error"
    WARNING = "warning"


class IssueCode(StrEnum):
    """Stable codes: never rename one once released.

    `FILE_TOO_LARGE` from the spec is missing on purpose: only the upload raises it.
    """

    UNSUPPORTED_FILE_TYPE = "UNSUPPORTED_FILE_TYPE"
    EMPTY_FILE = "EMPTY_FILE"
    MALFORMED_CSV = "MALFORMED_CSV"
    NO_DATA_ROWS = "NO_DATA_ROWS"
    TOO_MANY_ROWS = "TOO_MANY_ROWS"
    TOO_MANY_COLUMNS = "TOO_MANY_COLUMNS"
    MISSING_COLUMN = "MISSING_COLUMN"
    UNKNOWN_COLUMN = "UNKNOWN_COLUMN"
    MISSING_VALUE = "MISSING_VALUE"
    INVALID_TYPE = "INVALID_TYPE"
    INVALID_VALUE = "INVALID_VALUE"
    OUT_OF_RANGE = "OUT_OF_RANGE"
    DUPLICATE_SAMPLE_ID = "DUPLICATE_SAMPLE_ID"
    INCONSISTENT_REFERENCE = "INCONSISTENT_REFERENCE"


class ValidationIssue(BaseModel):
    """One problem found in a manifest."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    severity: Severity
    code: IssueCode
    message: str = Field(min_length=1)
    # File line number (the header is line 1). None for file- and header-level issues.
    row: int | None = Field(default=None, ge=2)
    # None for file-level issues and for a header cell that has no name.
    column: str | None = Field(default=None, min_length=1, max_length=MAX_COLUMN_NAME_LENGTH)
