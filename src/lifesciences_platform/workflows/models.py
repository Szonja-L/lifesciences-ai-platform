"""ORM models for Track A submission intake (spec: docs/architecture/track-a-spec.md).

Design notes (ADR 0004):
- `status` is a VARCHAR with a named check constraint, not a native Postgres ENUM.
  Only the Phase 1 states are allowed; later phases widen the constraint in a migration.
- `content_hash` is unique, so a repeated upload is refused by the database itself
  (the API turns that into HTTP 409 in task 1.2).
- `rule_set_version` is stored on the submission too: a clean file has no
  validation result rows, but must still record which rules it passed.
- Python attribute names avoid two clashes: `metadata` is reserved by SQLAlchemy's
  `Base`, and `column` is a reserved word in Postgres.
"""

import uuid
from datetime import datetime
from enum import StrEnum
from typing import Any

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Identity,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import CHAR, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from lifesciences_platform.common.db import Base

# Defined with the validation engine, which must not depend on the database (ADR 0006).
# The `as Severity` marks it as re-exported from here too.
from lifesciences_platform.common.validation.models import Severity as Severity


class SubmissionStatus(StrEnum):
    """Phase 1 states (spec section 3). Later phases add states with a migration."""

    SUBMITTED = "SUBMITTED"
    VALIDATED = "VALIDATED"
    VALIDATION_FAILED = "VALIDATION_FAILED"


def _in_list_sql(column: str, values: list[str]) -> str:
    quoted = ", ".join(f"'{value}'" for value in values)
    return f"{column} IN ({quoted})"


STATUS_CHECK_SQL = _in_list_sql("status", [s.value for s in SubmissionStatus])
SEVERITY_CHECK_SQL = _in_list_sql("severity", [s.value for s in Severity])


class Submission(Base):
    """One uploaded manifest plus the metadata sent with it. Never edited after validation."""

    __tablename__ = "submissions"
    __table_args__ = (
        CheckConstraint(STATUS_CHECK_SQL, name="status_allowed"),
        CheckConstraint("size_bytes >= 0", name="size_bytes_non_negative"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    filename: Mapped[str] = mapped_column(String(255))
    content_hash: Mapped[str] = mapped_column(CHAR(64), unique=True)  # SHA-256, hex
    size_bytes: Mapped[int] = mapped_column(BigInteger)
    status: Mapped[str] = mapped_column(String(32), default=SubmissionStatus.SUBMITTED.value)
    # Null until the file has been validated.
    rule_set_version: Mapped[str | None] = mapped_column(String(16))
    # The form fields from spec section 4.2, stored as JSON. Column name "metadata".
    submission_metadata: Mapped[dict[str, Any]] = mapped_column("metadata", JSONB)

    validation_results: Mapped[list["ValidationResult"]] = relationship(
        back_populates="submission",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="ValidationResult.id",
    )


class ValidationResult(Base):
    """One issue found while validating a submission (spec section 9)."""

    __tablename__ = "validation_results"
    __table_args__ = (
        CheckConstraint(SEVERITY_CHECK_SQL, name="severity_allowed"),
        # Line 1 is the header, so a data row is line 2 or later. Null = file/header level.
        CheckConstraint("row_number IS NULL OR row_number >= 2", name="row_number_data_line"),
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    submission_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("submissions.id", ondelete="CASCADE"), index=True
    )
    rule_set_version: Mapped[str] = mapped_column(String(16))
    severity: Mapped[str] = mapped_column(String(16))
    # Stable issue code such as MISSING_VALUE. Checked in Python, not in the database,
    # because new codes will be added with new rule set versions.
    code: Mapped[str] = mapped_column(String(64))
    message: Mapped[str] = mapped_column(Text)
    row_number: Mapped[int | None] = mapped_column(Integer)  # file line number
    column_name: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    submission: Mapped[Submission] = relationship(back_populates="validation_results")
