"""The API starts and /health answers."""

from fastapi.testclient import TestClient

import lifesciences_platform
from lifesciences_platform.api.main import create_app


def test_health_returns_ok_and_version() -> None:
    client = TestClient(create_app())
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "version": lifesciences_platform.__version__}


def test_health_exposes_nothing_else() -> None:
    body = TestClient(create_app()).get("/health").json()
    assert set(body) == {"status", "version"}


def test_unknown_route_is_404() -> None:
    assert TestClient(create_app()).get("/nope").status_code == 404
