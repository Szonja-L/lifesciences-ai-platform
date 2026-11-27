"""Intake rules that need no database: names, types, size limit, file storage, metadata."""

import hashlib
import io
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from lifesciences_platform.workflows import intake

VALID_METADATA: dict[str, Any] = {
    "client_id": "C-001",
    "project_name": "Synthetic exome batch A",
    "requested_analysis": "variant_annotation",
    "contact_email": "lab-contact@example.org",
}


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("valid.csv", "valid.csv"),
        ("../../etc/valid.csv", "valid.csv"),
        ("C:\\Users\\someone\\valid.csv", "valid.csv"),
    ],
)
def test_filename_keeps_only_the_last_part(raw: str, expected: str) -> None:
    assert intake.clean_filename(raw) == expected


@pytest.mark.parametrize("raw", [None, "", "folder/", "a" * 252 + ".csv", "bad\x00name.csv"])
def test_unusable_filenames_are_rejected(raw: str | None) -> None:
    with pytest.raises(intake.InvalidFilenameError):
        intake.clean_filename(raw)


@pytest.mark.parametrize(
    ("filename", "content_type"),
    [
        ("a.csv", "text/csv"),
        ("A.CSV", "text/csv; charset=utf-8"),
        ("a.csv", "application/vnd.ms-excel"),
    ],
)
def test_csv_types_are_accepted(filename: str, content_type: str) -> None:
    intake.check_file_type(filename, content_type)


@pytest.mark.parametrize(
    ("filename", "content_type"),
    [
        ("a.txt", "text/csv"),
        ("a.csv.exe", "text/csv"),
        ("a.csv", "text/plain"),
        ("a.csv", "application/octet-stream"),
        ("a.csv", None),
    ],
)
def test_other_types_are_rejected(filename: str, content_type: str | None) -> None:
    with pytest.raises(intake.UnsupportedFileTypeError):
        intake.check_file_type(filename, content_type)


def test_size_limit_is_inclusive() -> None:
    assert intake.read_limited(io.BytesIO(b"12345"), max_bytes=5) == b"12345"
    with pytest.raises(intake.FileTooLargeError):
        intake.read_limited(io.BytesIO(b"123456"), max_bytes=5)


def test_empty_stream_is_read_as_empty() -> None:
    assert intake.read_limited(io.BytesIO(b""), max_bytes=5) == b""


def test_store_file_writes_hash_named_file_and_no_leftovers(tmp_path: Path) -> None:
    content = b"sample_id\nS-0001\n"
    digest = hashlib.sha256(content).hexdigest()
    upload_dir = tmp_path / "uploads"

    intake.store_file(upload_dir, digest, content)
    target = intake.store_file(upload_dir, digest, content)  # storing again is harmless

    assert target == upload_dir / f"{digest}.csv"
    assert target.read_bytes() == content
    assert list(upload_dir.iterdir()) == [target]


def test_valid_metadata_is_trimmed() -> None:
    metadata = intake.SubmissionMetadata.model_validate(
        {**VALID_METADATA, "project_name": "  Batch A  "}
    )
    assert metadata.project_name == "Batch A"


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("client_id", "C-1"),
        ("client_id", "c-001"),
        ("project_name", "   "),
        ("project_name", "x" * 101),
        ("project_name", "bad\x00name"),
        ("requested_analysis", "genome_assembly"),
        ("contact_email", "not-an-email"),
    ],
)
def test_invalid_metadata_is_rejected(field: str, value: str) -> None:
    with pytest.raises(ValidationError):
        intake.SubmissionMetadata.model_validate({**VALID_METADATA, field: value})
