"""A database that cannot be reached gives a clear 503. Needs no running database."""

from collections.abc import Iterator
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from lifesciences_platform.api.dependencies import get_session
from lifesciences_platform.api.main import create_app
from lifesciences_platform.common.config import Settings, get_settings
from lifesciences_platform.common.db import create_db_engine

# Port 1 has nothing listening on it.
UNREACHABLE_URL = "postgresql+psycopg://someone:not-a-real-password@127.0.0.1:1/nowhere"


def test_unreachable_database_is_503_without_connection_details(tmp_path: Path) -> None:
    settings = Settings.model_validate({"database_url": UNREACHABLE_URL, "upload_dir": tmp_path})
    engine = create_db_engine(settings)

    def broken_session() -> Iterator[Session]:
        with Session(bind=engine) as db_session:
            yield db_session

    app = create_app()
    app.dependency_overrides[get_session] = broken_session
    app.dependency_overrides[get_settings] = lambda: settings

    response = TestClient(app).post(
        "/submissions",
        files={"file": ("valid.csv", b"sample_id\n", "text/csv")},
        data={
            "client_id": "C-001",
            "project_name": "Synthetic exome batch A",
            "requested_analysis": "variant_annotation",
            "contact_email": "lab-contact@example.org",
        },
    )

    assert response.status_code == 503
    assert response.json()["detail"]["code"] == "DATABASE_UNAVAILABLE"
    assert "not-a-real-password" not in response.text
    assert "127.0.0.1" not in response.text
    assert list(tmp_path.iterdir()) == []

    client = TestClient(app)
    for url in ("/submissions", "/submissions/00000000-0000-0000-0000-000000000000"):
        read = client.get(url)
        assert read.status_code == 503, url
        assert read.json()["detail"]["code"] == "DATABASE_UNAVAILABLE"
