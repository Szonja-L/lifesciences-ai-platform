"""FastAPI application (run: uvicorn lifesciences_platform.api.main:app --reload)."""

from typing import Literal

from fastapi import FastAPI
from pydantic import BaseModel

from lifesciences_platform import __version__


class HealthResponse(BaseModel):
    status: Literal["ok"]
    version: str


def create_app() -> FastAPI:
    """Build the app. A factory lets tests create a fresh instance."""
    application = FastAPI(title="Life Sciences AI Platform", version=__version__)

    @application.get("/health", response_model=HealthResponse)
    def health() -> HealthResponse:
        # Liveness only. Deliberately returns no settings, paths or secrets.
        return HealthResponse(status="ok", version=__version__)

    return application


app = create_app()
