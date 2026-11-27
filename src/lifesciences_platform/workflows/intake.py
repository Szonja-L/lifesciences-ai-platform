"""Submission intake: check an uploaded file at the door, store it, record it.

Spec: docs/architecture/track-a-spec.md sections 4, 6 and 7. Storage design: ADR 0005.
This module knows nothing about HTTP. It raises `IntakeError` subclasses and the API
layer turns them into responses. It does not look inside the file: an empty or broken
CSV is accepted here and rejected by validation (`workflows.validate_submission`).
"""

import hashlib
import tempfile
import uuid
from enum import StrEnum
from pathlib import Path
from typing import BinaryIO

import psycopg
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from lifesciences_platform.workflows.models import Submission, SubmissionStatus

STORED_EXTENSION = ".csv"
# application/vnd.ms-excel is what some browsers send for a CSV file.
ALLOWED_CONTENT_TYPES = frozenset({"text/csv", "application/vnd.ms-excel"})
MAX_FILENAME_LENGTH = 255  # length of submissions.filename
READ_CHUNK_BYTES = 64 * 1024
DUPLICATE_CONSTRAINT = "uq_submissions_content_hash"


class RequestedAnalysis(StrEnum):
    VARIANT_CALLING_QC = "variant_calling_qc"
    VARIANT_ANNOTATION = "variant_annotation"


class SubmissionMetadata(BaseModel):
    """The form fields sent with a file (spec section 4.2)."""

    model_config = ConfigDict(str_strip_whitespace=True)

    client_id: str = Field(pattern=r"^C-[0-9]{3}$")
    project_name: str = Field(min_length=1, max_length=100)
    requested_analysis: RequestedAnalysis
    contact_email: EmailStr

    @field_validator("project_name")
    @classmethod
    def _no_control_characters(cls, value: str) -> str:
        # Postgres JSONB cannot store a NUL character; refuse it here with a clear message.
        if not value.isprintable():
            raise ValueError("must not contain control characters")
        return value


class IntakeError(Exception):
    """An upload was refused. `code` is stable; `message` is safe to show the client."""

    code: str

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class InvalidFilenameError(IntakeError):
    code = "INVALID_FILENAME"


class UnsupportedFileTypeError(IntakeError):
    code = "UNSUPPORTED_FILE_TYPE"


class FileTooLargeError(IntakeError):
    code = "FILE_TOO_LARGE"


class DuplicateFileError(IntakeError):
    code = "DUPLICATE_FILE"

    def __init__(self, existing_id: uuid.UUID | None) -> None:
        super().__init__("This exact file has already been submitted.")
        self.existing_id = existing_id


class StorageUnavailableError(IntakeError):
    code = "STORAGE_UNAVAILABLE"


def clean_filename(raw: str | None) -> str:
    """Keep only the last path part. The name is recorded, never used to build a path."""
    name = (raw or "").replace("\\", "/").rsplit("/", 1)[-1].strip()
    if not name:
        raise InvalidFilenameError("The uploaded file has no name.")
    if len(name) > MAX_FILENAME_LENGTH or not name.isprintable():
        raise InvalidFilenameError(
            f"The file name must be at most {MAX_FILENAME_LENGTH} printable characters."
        )
    return name


def check_file_type(filename: str, content_type: str | None) -> None:
    """Both the extension and the declared content type must say CSV."""
    if not filename.lower().endswith(STORED_EXTENSION):
        raise UnsupportedFileTypeError(f"Only {STORED_EXTENSION} files are accepted.")
    # Drop parameters such as "; charset=utf-8".
    media_type = (content_type or "").split(";", 1)[0].strip().lower()
    if media_type not in ALLOWED_CONTENT_TYPES:
        allowed = ", ".join(sorted(ALLOWED_CONTENT_TYPES))
        raise UnsupportedFileTypeError(
            f"Content type {media_type or '(none)'!r} is not accepted; send one of: {allowed}."
        )


def read_limited(stream: BinaryIO, max_bytes: int) -> bytes:
    """Read the whole stream, stopping as soon as it is known to exceed the limit."""
    content = bytearray()
    while chunk := stream.read(READ_CHUNK_BYTES):
        content += chunk
        if len(content) > max_bytes:
            raise FileTooLargeError(f"The file is larger than the limit of {max_bytes} bytes.")
    return bytes(content)


def stored_path(upload_dir: Path, content_hash: str) -> Path:
    """Where the file with this hash is kept (ADR 0005)."""
    return upload_dir / f"{content_hash}{STORED_EXTENSION}"


def store_file(upload_dir: Path, content_hash: str, content: bytes) -> Path:
    """Write `<hash>.csv` so that it is either complete or absent, never half written."""
    upload_dir.mkdir(parents=True, exist_ok=True)
    target = stored_path(upload_dir, content_hash)
    with tempfile.NamedTemporaryFile(dir=upload_dir, suffix=".tmp", delete=False) as handle:
        temporary = Path(handle.name)
    try:
        temporary.write_bytes(content)
        temporary.replace(target)
    finally:
        temporary.unlink(missing_ok=True)  # already gone when the rename succeeded
    return target


def create_submission(
    session: Session,
    *,
    filename: str,
    content: bytes,
    metadata: SubmissionMetadata,
    upload_dir: Path,
) -> Submission:
    """Insert the row, store the file, then commit (the order is explained in ADR 0005)."""
    content_hash = hashlib.sha256(content).hexdigest()
    submission = Submission(
        filename=filename,
        content_hash=content_hash,
        size_bytes=len(content),
        status=SubmissionStatus.SUBMITTED.value,
        submission_metadata=metadata.model_dump(mode="json"),
    )
    session.add(submission)
    try:
        session.flush()  # the unique constraint rejects a duplicate here
    except IntegrityError as error:
        session.rollback()
        if not _is_duplicate_file(error):
            raise
        existing_id = session.scalar(
            select(Submission.id).where(Submission.content_hash == content_hash)
        )
        raise DuplicateFileError(existing_id) from error

    try:
        store_file(upload_dir, content_hash, content)
    except OSError as error:
        session.rollback()
        raise StorageUnavailableError("The file could not be stored. Try again later.") from error

    session.commit()
    return submission


def _is_duplicate_file(error: IntegrityError) -> bool:
    original = error.orig
    return (
        isinstance(original, psycopg.errors.UniqueViolation)
        and original.diag.constraint_name == DUPLICATE_CONSTRAINT
    )
