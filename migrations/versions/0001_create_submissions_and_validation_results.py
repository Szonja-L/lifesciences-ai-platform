"""Create submissions and validation_results (task 1.1, ADR 0004).

Generated with `alembic revision --autogenerate`, then reviewed by hand.

Revision ID: 0001
Revises:
Create Date: 2026-11-25 15:45:24.701598

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0001"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "submissions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("content_hash", sa.CHAR(length=64), nullable=False),
        sa.Column("size_bytes", sa.BigInteger(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("rule_set_version", sa.String(length=16), nullable=True),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.CheckConstraint(
            "status IN ('SUBMITTED', 'VALIDATED', 'VALIDATION_FAILED')",
            name=op.f("ck_submissions_status_allowed"),
        ),
        sa.CheckConstraint("size_bytes >= 0", name=op.f("ck_submissions_size_bytes_non_negative")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_submissions")),
        sa.UniqueConstraint("content_hash", name=op.f("uq_submissions_content_hash")),
    )
    op.create_table(
        "validation_results",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=False), nullable=False),
        sa.Column("submission_id", sa.Uuid(), nullable=False),
        sa.Column("rule_set_version", sa.String(length=16), nullable=False),
        sa.Column("severity", sa.String(length=16), nullable=False),
        sa.Column("code", sa.String(length=64), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("row_number", sa.Integer(), nullable=True),
        sa.Column("column_name", sa.String(length=255), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "severity IN ('error', 'warning')", name=op.f("ck_validation_results_severity_allowed")
        ),
        sa.CheckConstraint(
            "row_number IS NULL OR row_number >= 2",
            name=op.f("ck_validation_results_row_number_data_line"),
        ),
        sa.ForeignKeyConstraint(
            ["submission_id"],
            ["submissions.id"],
            name=op.f("fk_validation_results_submission_id_submissions"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_validation_results")),
    )
    op.create_index(
        op.f("ix_validation_results_submission_id"),
        "validation_results",
        ["submission_id"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_validation_results_submission_id"), table_name="validation_results")
    op.drop_table("validation_results")
    op.drop_table("submissions")
