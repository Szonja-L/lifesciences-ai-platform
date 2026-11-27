"""Validate a stored submission and record the outcome (ADR 0007).

Runs after intake has committed the row, in a transaction of its own. If anything fails
here, the submission stays SUBMITTED with no results, for staff to look at (spec section
6). It is never marked valid by accident, and never half recorded.
"""

import logging
import traceback
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from sqlalchemy.orm import Session

from lifesciences_platform.common.validation import (
    RULE_SET_V1,
    RuleSet,
    Severity,
    validate_manifest,
)
from lifesciences_platform.workflows.models import Submission, SubmissionStatus, ValidationResult

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ValidationOutcome:
    status: SubmissionStatus
    rule_set_version: str | None  # None when validation did not complete


def validate_submission(
    session: Session,
    submission: Submission,
    *,
    path: Path,
    today: date,
    max_rows: int,
    rule_set: RuleSet = RULE_SET_V1,
) -> ValidationOutcome:
    """Check the file, store every issue, set the status and commit."""
    submission_id = submission.id  # read now: a rollback expires the object
    try:
        issues = validate_manifest(path, rule_set, today=today, max_rows=max_rows)
        session.add_all(
            ValidationResult(
                submission_id=submission_id,
                rule_set_version=rule_set.version,
                severity=issue.severity.value,
                code=str(issue.code),
                message=issue.message,
                row_number=issue.row,
                column_name=issue.column,
            )
            for issue in issues
        )
        has_errors = any(issue.severity is Severity.ERROR for issue in issues)
        status = SubmissionStatus.VALIDATION_FAILED if has_errors else SubmissionStatus.VALIDATED
        submission.status = status.value
        submission.rule_set_version = rule_set.version
        session.commit()
    except Exception as error:  # deliberately broad: any failure must leave SUBMITTED
        session.rollback()
        # The exception message is left out: it can quote values from the client's file.
        logger.error(
            "Validation of submission %s failed with %s; it stays SUBMITTED.\n%s",
            submission_id,
            type(error).__name__,
            "".join(traceback.format_tb(error.__traceback__)),
        )
        return ValidationOutcome(status=SubmissionStatus.SUBMITTED, rule_set_version=None)
    return ValidationOutcome(status=status, rule_set_version=rule_set.version)
