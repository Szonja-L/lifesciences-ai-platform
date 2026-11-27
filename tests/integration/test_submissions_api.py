"""`POST /submissions` through the API, against the real database.

File contents are unique per test, so a file uploaded by hand to the local database
(for example with the README curl command) cannot cause a false 409.
"""

import hashlib
import uuid
from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from httpx import Response
from sqlalchemy import Connection, delete, func, select
from sqlalchemy.orm import Session

from lifesciences_platform.api.dependencies import get_session
from lifesciences_platform.api.main import create_app
from lifesciences_platform.common.config import Settings, get_settings
from lifesciences_platform.workflows.models import Submission

pytestmark = pytest.mark.db

MAX_BYTES = 1024
FORM = {
    "client_id": "C-001",
    "project_name": "Synthetic exome batch A",
    "requested_analysis": "variant_annotation",
    "contact_email": "lab-contact@example.org",
}


def unique_content() -> bytes:
    return f"sample_id\n{uuid.uuid4().hex}\n".encode()


@pytest.fixture
def upload_dir(tmp_path: Path) -> Path:
    return tmp_path / "uploads"


@pytest.fixture
def app(db_connection: Connection, upload_dir: Path) -> FastAPI:
    application = create_app()
    settings = Settings(upload_dir=upload_dir, max_upload_bytes=MAX_BYTES)

    def session_in_test_transaction() -> Iterator[Session]:
        with Session(
            bind=db_connection,
            join_transaction_mode="create_savepoint",
            expire_on_commit=False,
        ) as db_session:
            yield db_session

    application.dependency_overrides[get_session] = session_in_test_transaction
    application.dependency_overrides[get_settings] = lambda: settings
    return application


@pytest.fixture
def client(app: FastAPI) -> TestClient:
    return TestClient(app)


def upload(
    client: TestClient,
    content: bytes,
    filename: str = "valid.csv",
    content_type: str = "text/csv",
    form: dict[str, str] | None = None,
) -> Response:
    # Annotated because TestClient's base class is untyped to mypy here.
    response: Response = client.post(
        "/submissions",
        files={"file": (filename, content, content_type)},
        data=FORM if form is None else form,
    )
    return response


def rows_with_content(session: Session, content: bytes) -> int:
    digest = hashlib.sha256(content).hexdigest()
    count = session.scalar(
        select(func.count()).select_from(Submission).where(Submission.content_hash == digest)
    )
    return count or 0


def assert_nothing_created(session: Session, upload_dir: Path, content: bytes) -> None:
    assert rows_with_content(session, content) == 0
    assert not upload_dir.exists() or list(upload_dir.iterdir()) == []


def test_valid_upload_creates_row_and_file(
    client: TestClient, session: Session, upload_dir: Path
) -> None:
    content = unique_content()
    digest = hashlib.sha256(content).hexdigest()

    response = upload(client, content)

    assert response.status_code == 201, response.text
    body = response.json()
    assert body["status"] == "SUBMITTED"
    assert body["filename"] == "valid.csv"
    assert body["content_hash"] == digest
    assert body["size_bytes"] == len(content)
    assert (upload_dir / f"{digest}.csv").read_bytes() == content
    stored = session.get(Submission, uuid.UUID(body["id"]))
    assert stored is not None
    assert stored.submission_metadata == FORM
    assert stored.rule_set_version is None  # not validated yet


def test_zero_byte_file_is_accepted_for_validation_to_judge(
    client: TestClient, session: Session
) -> None:
    # Every zero-byte file has the same hash, so remove any row left by manual testing.
    # This happens inside the rolled-back test transaction: local data is not changed.
    empty_hash = hashlib.sha256(b"").hexdigest()
    session.execute(delete(Submission).where(Submission.content_hash == empty_hash))
    session.commit()

    response = upload(client, b"", filename="empty.csv")

    assert response.status_code == 201, response.text
    assert response.json()["size_bytes"] == 0
    assert response.json()["status"] == "SUBMITTED"


def test_duplicate_file_is_409_and_points_to_the_first(
    client: TestClient, session: Session
) -> None:
    content = unique_content()
    first = upload(client, content)

    second = upload(client, content, filename="renamed.csv")

    assert second.status_code == 409
    detail = second.json()["detail"]
    assert detail["code"] == "DUPLICATE_FILE"
    assert detail["existing_submission_id"] == first.json()["id"]
    assert rows_with_content(session, content) == 1


def test_oversize_file_is_413(client: TestClient, session: Session, upload_dir: Path) -> None:
    content = unique_content() + b"x" * MAX_BYTES

    response = upload(client, content)

    assert response.status_code == 413
    assert response.json()["detail"]["code"] == "FILE_TOO_LARGE"
    assert str(MAX_BYTES) in response.json()["detail"]["message"]
    assert_nothing_created(session, upload_dir, content)


@pytest.mark.parametrize(
    ("filename", "content_type"),
    [("unsupported_type.txt", "text/plain"), ("valid.csv", "application/octet-stream")],
)
def test_wrong_type_is_415(
    client: TestClient, session: Session, upload_dir: Path, filename: str, content_type: str
) -> None:
    content = unique_content()

    response = upload(client, content, filename=filename, content_type=content_type)

    assert response.status_code == 415
    assert response.json()["detail"]["code"] == "UNSUPPORTED_FILE_TYPE"
    assert_nothing_created(session, upload_dir, content)


def test_empty_request_body_is_422(client: TestClient) -> None:
    response = client.post("/submissions")

    assert response.status_code == 422
    missing = {issue["loc"][-1] for issue in response.json()["detail"]}
    assert missing == {"file", *FORM}


def test_missing_file_is_422(client: TestClient) -> None:
    response = client.post("/submissions", data=FORM)

    assert response.status_code == 422
    assert [issue["loc"][-1] for issue in response.json()["detail"]] == ["file"]


@pytest.mark.parametrize(
    ("field", "value"),
    [("client_id", "ACME"), ("contact_email", "nobody"), ("requested_analysis", "other")],
)
def test_invalid_metadata_is_422_and_names_the_field(
    client: TestClient, session: Session, upload_dir: Path, field: str, value: str
) -> None:
    content = unique_content()

    response = upload(client, content, form={**FORM, field: value})

    assert response.status_code == 422
    assert [issue["loc"] for issue in response.json()["detail"]] == [["body", field]]
    assert_nothing_created(session, upload_dir, content)


def test_storage_failure_is_503_and_leaves_no_row(
    app: FastAPI, session: Session, tmp_path: Path
) -> None:
    not_a_folder = tmp_path / "taken"
    not_a_folder.write_text("a file where the upload folder should be")
    app.dependency_overrides[get_settings] = lambda: Settings(upload_dir=not_a_folder)
    content = unique_content()

    response = upload(TestClient(app), content)

    assert response.status_code == 503
    assert response.json()["detail"]["code"] == "STORAGE_UNAVAILABLE"
    assert str(tmp_path) not in response.text  # no server paths in the answer
    assert rows_with_content(session, content) == 0
