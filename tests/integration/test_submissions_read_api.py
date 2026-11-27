"""Validation on upload and the two read endpoints, against the real database."""

import hashlib
import logging
import uuid
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient
from httpx import Response
from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from lifesciences_platform.common.config import Settings
from lifesciences_platform.common.validation import IssueCode, Severity, ValidationIssue
from lifesciences_platform.workflows import validate_submission as validation_step
from lifesciences_platform.workflows.models import Submission, ValidationResult

pytestmark = pytest.mark.db

FIXTURES = Path(__file__).parents[1] / "fixtures" / "manifests"
FORM = {
    "client_id": "C-001",
    "project_name": "Synthetic exome batch A",
    "requested_analysis": "variant_annotation",
    "contact_email": "lab-contact@example.org",
}


def forget(session: Session, content: bytes) -> None:
    """Remove a row left by manual testing. Rolled back with the test: nothing is lost."""
    digest = hashlib.sha256(content).hexdigest()
    session.execute(delete(Submission).where(Submission.content_hash == digest))
    session.commit()


def upload(client: TestClient, session: Session, content: bytes) -> dict[str, Any]:
    forget(session, content)
    response: Response = client.post(
        "/submissions", files={"file": ("manifest.csv", content, "text/csv")}, data=FORM
    )
    assert response.status_code == 201, response.text
    body: dict[str, Any] = response.json()
    return body


def detail(client: TestClient, submission_id: str) -> dict[str, Any]:
    response: Response = client.get(f"/submissions/{submission_id}")
    assert response.status_code == 200, response.text
    body: dict[str, Any] = response.json()
    return body


def stored_results(session: Session, submission_id: str) -> int:
    count = session.scalar(
        select(func.count())
        .select_from(ValidationResult)
        .where(ValidationResult.submission_id == uuid.UUID(submission_id))
    )
    return count or 0


def valid_manifest_with_unique_label() -> bytes:
    """The valid fixture with one label changed, so its hash is new."""
    text = (FIXTURES / "valid.csv").read_text(encoding="utf-8")
    return text.replace("ctrl_rep1", uuid.uuid4().hex).encode()


# ------------------------------------------------------------------ validation on upload


def test_valid_manifest_is_validated(client: TestClient, session: Session) -> None:
    created = upload(client, session, (FIXTURES / "valid.csv").read_bytes())

    assert created["status"] == "VALIDATED"
    assert created["rule_set_version"] == "v1"
    body = detail(client, created["id"])
    assert body["status"] == "VALIDATED"
    assert body["rule_set_version"] == "v1"
    assert body["metadata"] == FORM
    assert body["issues"] == []


def test_missing_columns_fail_and_are_stored(client: TestClient, session: Session) -> None:
    created = upload(client, session, (FIXTURES / "missing_columns.csv").read_bytes())

    assert created["status"] == "VALIDATION_FAILED"
    issues = detail(client, created["id"])["issues"]
    assert [(i["code"], i["column"], i["row"]) for i in issues] == [
        ("MISSING_COLUMN", "assay", None),
        ("MISSING_COLUMN", "collection_date", None),
    ]
    assert {i["severity"] for i in issues} == {"error"}
    assert {i["rule_set_version"] for i in issues} == {"v1"}
    assert all(i["message"] for i in issues)
    assert stored_results(session, created["id"]) == 2


def test_warnings_alone_do_not_block(client: TestClient, session: Session) -> None:
    header, *rows = valid_manifest_with_unique_label().decode().splitlines()
    content = "\n".join([f"{header},notes", *(f"{row},x" for row in rows)]).encode()

    created = upload(client, session, content)

    assert created["status"] == "VALIDATED"
    issues = detail(client, created["id"])["issues"]
    assert [(i["code"], i["severity"]) for i in issues] == [("UNKNOWN_COLUMN", "warning")]


def test_row_limit_comes_from_settings(
    client: TestClient, session: Session, settings: Settings
) -> None:
    settings.max_manifest_rows = 1

    created = upload(client, session, valid_manifest_with_unique_label())

    assert created["status"] == "VALIDATION_FAILED"
    assert [i["code"] for i in detail(client, created["id"])["issues"]] == ["TOO_MANY_ROWS"]


def assert_left_submitted(client: TestClient, session: Session, created: dict[str, Any]) -> None:
    assert created["status"] == "SUBMITTED"
    assert created["rule_set_version"] is None
    body = detail(client, created["id"])
    assert body["status"] == "SUBMITTED"
    assert body["rule_set_version"] is None
    assert body["issues"] == []
    assert stored_results(session, created["id"]) == 0


def test_engine_crash_leaves_the_submission_submitted(
    client: TestClient,
    session: Session,
    upload_dir: Path,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    # A variable, because the logged stack frames show the source line that raises.
    client_text = "text copied from the client's file"

    def crash(*args: object, **kwargs: object) -> list[ValidationIssue]:
        raise RuntimeError(client_text)

    monkeypatch.setattr(validation_step, "validate_manifest", crash)
    content = valid_manifest_with_unique_label()

    with caplog.at_level(logging.ERROR):
        created = upload(client, session, content)

    assert_left_submitted(client, session, created)
    assert (upload_dir / f"{created['content_hash']}.csv").read_bytes() == content
    assert created["id"] in caplog.text
    assert "RuntimeError" in caplog.text
    assert client_text not in caplog.text


def test_failure_while_saving_results_stores_none_of_them(
    client: TestClient,
    session: Session,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    storable = ValidationIssue(severity=Severity.ERROR, code=IssueCode.EMPTY_FILE, message="x")
    # Built without Pydantic's checks: the code is too long for its database column.
    unstorable = ValidationIssue.model_construct(
        severity=Severity.ERROR,
        code="X" * 65,  # type: ignore[arg-type]
        message="x",
        row=None,
        column=None,
    )
    monkeypatch.setattr(
        validation_step, "validate_manifest", lambda *args, **kwargs: [storable, unstorable]
    )

    with caplog.at_level(logging.ERROR):
        created = upload(client, session, valid_manifest_with_unique_label())

    assert_left_submitted(client, session, created)
    assert "DataError" in caplog.text  # it was the database that refused


# ------------------------------------------------------------------ list


def add_submission(session: Session, created_at: datetime) -> str:
    submission = Submission(
        created_at=created_at,
        filename="listed.csv",
        content_hash=hashlib.sha256(uuid.uuid4().bytes).hexdigest(),
        size_bytes=1,
        submission_metadata=FORM,
    )
    session.add(submission)
    session.commit()
    return str(submission.id)


def test_list_is_paginated_newest_first(client: TestClient, session: Session) -> None:
    before = client.get("/submissions").json()["total"]
    # Far in the future, so they sort ahead of anything already in a local database.
    start = datetime(2999, 1, 1, tzinfo=UTC)
    oldest, middle, newest = (add_submission(session, start + timedelta(days=n)) for n in range(3))

    first = client.get("/submissions", params={"limit": 2}).json()
    second = client.get("/submissions", params={"limit": 2, "offset": 2}).json()

    assert (first["total"], first["limit"], first["offset"]) == (before + 3, 2, 0)
    assert [item["id"] for item in first["items"]] == [newest, middle]
    assert second["offset"] == 2
    assert second["items"][0]["id"] == oldest
    assert "metadata" not in first["items"][0]
    assert FORM["contact_email"] not in str(first)


def test_list_past_the_end_is_empty(client: TestClient) -> None:
    body = client.get("/submissions", params={"offset": 2**31 - 1}).json()

    assert body["items"] == []
    assert body["limit"] == 20


@pytest.mark.parametrize(
    "params", [{"limit": 0}, {"limit": 101}, {"offset": -1}, {"offset": 2**63}, {"limit": "all"}]
)
def test_list_refuses_bad_paging(client: TestClient, params: dict[str, Any]) -> None:
    assert client.get("/submissions", params=params).status_code == 422


# ------------------------------------------------------------------ detail


def test_unknown_id_is_404(client: TestClient) -> None:
    response = client.get(f"/submissions/{uuid.uuid4()}")

    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "SUBMISSION_NOT_FOUND"


def test_id_that_is_not_a_uuid_is_422(client: TestClient) -> None:
    assert client.get("/submissions/1").status_code == 422


# ------------------------------------------------------------------ documentation


def test_openapi_lists_the_three_endpoints_and_no_others(client: TestClient) -> None:
    paths = client.get("/openapi.json").json()["paths"]

    operations = {
        (path, method) for path, item in paths.items() if "submissions" in path for method in item
    }
    assert operations == {
        ("/submissions", "post"),
        ("/submissions", "get"),
        ("/submissions/{submission_id}", "get"),
    }
    assert all(paths[path][method]["summary"] for path, method in operations)
    assert "404" in paths["/submissions/{submission_id}"]["get"]["responses"]
