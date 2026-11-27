"""`POST /submissions`: the HTTP side of intake. The rules live in `workflows.intake`."""

import logging
import uuid
from datetime import datetime
from http import HTTPStatus
from typing import Annotated, Any

from fastapi import APIRouter, Depends, FastAPI, File, Form, Request, UploadFile
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, ValidationError
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from lifesciences_platform.api.dependencies import get_session
from lifesciences_platform.common.config import Settings, get_settings
from lifesciences_platform.common.db import DatabaseNotConfiguredError
from lifesciences_platform.workflows import intake
from lifesciences_platform.workflows.models import SubmissionStatus

logger = logging.getLogger(__name__)

router = APIRouter(tags=["submissions"])


class SubmissionCreated(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    status: SubmissionStatus
    filename: str
    content_hash: str
    size_bytes: int
    created_at: datetime


class ErrorDetail(BaseModel):
    code: str
    message: str
    existing_submission_id: uuid.UUID | None = None


class ErrorResponse(BaseModel):
    detail: ErrorDetail


STATUS_BY_ERROR: dict[type[intake.IntakeError], HTTPStatus] = {
    intake.InvalidFilenameError: HTTPStatus.UNPROCESSABLE_ENTITY,
    intake.UnsupportedFileTypeError: HTTPStatus.UNSUPPORTED_MEDIA_TYPE,
    intake.FileTooLargeError: HTTPStatus.REQUEST_ENTITY_TOO_LARGE,
    intake.DuplicateFileError: HTTPStatus.CONFLICT,
    intake.StorageUnavailableError: HTTPStatus.SERVICE_UNAVAILABLE,
}

ERROR_RESPONSES: dict[int | str, dict[str, Any]] = {
    int(code): {"model": ErrorResponse}
    for code in (
        HTTPStatus.CONFLICT,
        HTTPStatus.REQUEST_ENTITY_TOO_LARGE,
        HTTPStatus.UNSUPPORTED_MEDIA_TYPE,
        HTTPStatus.SERVICE_UNAVAILABLE,
    )
}


def metadata_from_form(
    client_id: Annotated[str, Form(description="C- followed by 3 digits, e.g. C-001")],
    project_name: Annotated[str, Form(description="1 to 100 characters")],
    requested_analysis: Annotated[intake.RequestedAnalysis, Form()],
    contact_email: Annotated[str, Form()],
) -> intake.SubmissionMetadata:
    """Validate the form fields together and answer failures with FastAPI's usual 422."""
    try:
        return intake.SubmissionMetadata.model_validate(
            {
                "client_id": client_id,
                "project_name": project_name,
                "requested_analysis": requested_analysis,
                "contact_email": contact_email,
            }
        )
    except ValidationError as error:
        raise RequestValidationError(
            [
                {**issue, "loc": ("body", *issue["loc"])}
                for issue in error.errors(include_url=False, include_context=False)
            ]
        ) from error


# A plain `def`: FastAPI runs it in a worker thread, so file and database work
# does not block the event loop.
@router.post(
    "/submissions",
    response_model=SubmissionCreated,
    status_code=HTTPStatus.CREATED,
    responses=ERROR_RESPONSES,
)
def create_submission(
    file: Annotated[UploadFile, File(description="Sample manifest, one CSV file")],
    metadata: Annotated[intake.SubmissionMetadata, Depends(metadata_from_form)],
    session: Annotated[Session, Depends(get_session)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> SubmissionCreated:
    filename = intake.clean_filename(file.filename)
    intake.check_file_type(filename, file.content_type)
    content = intake.read_limited(file.file, settings.max_upload_bytes)
    submission = intake.create_submission(
        session,
        filename=filename,
        content=content,
        metadata=metadata,
        upload_dir=settings.upload_dir,
    )
    return SubmissionCreated.model_validate(submission)


def _error_response(status: HTTPStatus, detail: ErrorDetail) -> JSONResponse:
    body = ErrorResponse(detail=detail).model_dump(mode="json", exclude_none=True)
    return JSONResponse(status_code=status, content=body)


def _handle_intake_error(request: Request, error: Exception) -> JSONResponse:
    assert isinstance(error, intake.IntakeError)
    if isinstance(error, intake.StorageUnavailableError):
        logger.error("Upload storage failed: %r", error.__cause__)
    existing_id = error.existing_id if isinstance(error, intake.DuplicateFileError) else None
    return _error_response(
        STATUS_BY_ERROR[type(error)],
        ErrorDetail(code=error.code, message=error.message, existing_submission_id=existing_id),
    )


def _handle_database_unavailable(request: Request, error: Exception) -> JSONResponse:
    # Only the class name is logged, and nothing about the connection is returned.
    logger.error("Database unavailable: %s", type(error).__name__)
    return _error_response(
        HTTPStatus.SERVICE_UNAVAILABLE,
        ErrorDetail(
            code="DATABASE_UNAVAILABLE", message="The database is unavailable. Try again later."
        ),
    )


def register_error_handlers(application: FastAPI) -> None:
    application.add_exception_handler(intake.IntakeError, _handle_intake_error)
    application.add_exception_handler(OperationalError, _handle_database_unavailable)
    application.add_exception_handler(DatabaseNotConfiguredError, _handle_database_unavailable)
