"""The `/submissions` routes: upload with validation, list and detail.

The HTTP side only. The rules live in `workflows.intake` and `workflows.validate_submission`.
"""

import logging
import uuid
from datetime import date, datetime
from http import HTTPStatus
from typing import Annotated, Any

from fastapi import (
    APIRouter,
    Depends,
    FastAPI,
    File,
    Form,
    HTTPException,
    Query,
    Request,
    UploadFile,
)
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, ValidationError
from sqlalchemy import func, select
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session, selectinload

from lifesciences_platform.api.dependencies import get_session, get_validation_date
from lifesciences_platform.common.config import Settings, get_settings
from lifesciences_platform.common.db import DatabaseNotConfiguredError
from lifesciences_platform.common.validation import Severity
from lifesciences_platform.workflows import intake
from lifesciences_platform.workflows.models import Submission, SubmissionStatus, ValidationResult
from lifesciences_platform.workflows.validate_submission import validate_submission

logger = logging.getLogger(__name__)

router = APIRouter(tags=["submissions"])

DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100
MAX_PAGE_OFFSET = 2**31 - 1  # refuse numbers the database cannot take


class SubmissionSummary(BaseModel):
    """A submission without its metadata and issues."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    status: SubmissionStatus
    filename: str
    content_hash: str
    size_bytes: int
    created_at: datetime
    rule_set_version: str | None  # null when the file has not been validated


class SubmissionPage(BaseModel):
    items: list[SubmissionSummary]
    total: int  # all submissions, not only this page
    limit: int
    offset: int


class Issue(BaseModel):
    severity: Severity
    code: str
    message: str
    row: int | None  # file line number; the header is line 1
    column: str | None
    rule_set_version: str


class SubmissionDetail(SubmissionSummary):
    updated_at: datetime
    # Returned as stored: tightening an upload rule must not make old records unreadable.
    metadata: dict[str, Any]
    issues: list[Issue]


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


def _documented_errors(*codes: HTTPStatus) -> dict[int | str, dict[str, Any]]:
    return {int(code): {"model": ErrorResponse} for code in codes}


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


# Plain `def` routes: FastAPI runs them in a worker thread, so file and database work
# does not block the event loop.
@router.post(
    "/submissions",
    response_model=SubmissionSummary,
    status_code=HTTPStatus.CREATED,
    summary="Upload and validate a manifest",
    responses=_documented_errors(
        HTTPStatus.CONFLICT,
        HTTPStatus.REQUEST_ENTITY_TOO_LARGE,
        HTTPStatus.UNSUPPORTED_MEDIA_TYPE,
        HTTPStatus.SERVICE_UNAVAILABLE,
    ),
)
def create_submission(
    file: Annotated[UploadFile, File(description="Sample manifest, one CSV file")],
    metadata: Annotated[intake.SubmissionMetadata, Depends(metadata_from_form)],
    session: Annotated[Session, Depends(get_session)],
    settings: Annotated[Settings, Depends(get_settings)],
    today: Annotated[date, Depends(get_validation_date)],
) -> SubmissionSummary:
    """Store the file, then validate it.

    201 means the file was accepted and recorded, not that it is valid: read `status`.
    `SUBMITTED` in the response means validation could not be completed.
    """
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
    # Copied before validating: after a rollback the row would have to be read again.
    stored = SubmissionSummary.model_validate(submission)
    outcome = validate_submission(
        session,
        submission,
        path=intake.stored_path(settings.upload_dir, stored.content_hash),
        today=today,
        max_rows=settings.max_manifest_rows,
    )
    return stored.model_copy(
        update={"status": outcome.status, "rule_set_version": outcome.rule_set_version}
    )


@router.get(
    "/submissions",
    response_model=SubmissionPage,
    summary="List submissions, newest first",
    responses=_documented_errors(HTTPStatus.SERVICE_UNAVAILABLE),
)
def list_submissions(
    session: Annotated[Session, Depends(get_session)],
    limit: Annotated[int, Query(ge=1, le=MAX_PAGE_SIZE)] = DEFAULT_PAGE_SIZE,
    offset: Annotated[int, Query(ge=0, le=MAX_PAGE_OFFSET)] = 0,
) -> SubmissionPage:
    """One page of submissions. Metadata and issues are in the detail endpoint."""
    total = session.scalar(select(func.count()).select_from(Submission)) or 0
    rows = session.scalars(
        select(Submission)
        # The id breaks ties, so pages do not overlap when times are equal.
        .order_by(Submission.created_at.desc(), Submission.id.desc())
        .limit(limit)
        .offset(offset)
    )
    items = [SubmissionSummary.model_validate(row) for row in rows]
    return SubmissionPage(items=items, total=total, limit=limit, offset=offset)


def _issue_from(result: ValidationResult) -> Issue:
    return Issue(
        severity=Severity(result.severity),
        code=result.code,
        message=result.message,
        row=result.row_number,
        column=result.column_name,
        rule_set_version=result.rule_set_version,
    )


@router.get(
    "/submissions/{submission_id}",
    response_model=SubmissionDetail,
    summary="One submission with its validation issues",
    responses=_documented_errors(HTTPStatus.NOT_FOUND, HTTPStatus.SERVICE_UNAVAILABLE),
)
def get_submission(
    submission_id: uuid.UUID,
    session: Annotated[Session, Depends(get_session)],
) -> SubmissionDetail:
    """The record, the metadata sent with it and every issue in the order it was found."""
    submission = session.get(
        Submission, submission_id, options=[selectinload(Submission.validation_results)]
    )
    if submission is None:
        detail = ErrorDetail(code="SUBMISSION_NOT_FOUND", message="No submission has this id.")
        raise HTTPException(HTTPStatus.NOT_FOUND, detail.model_dump(exclude_none=True))
    return SubmissionDetail(
        **SubmissionSummary.model_validate(submission).model_dump(),
        updated_at=submission.updated_at,
        metadata=submission.submission_metadata,
        issues=[_issue_from(result) for result in submission.validation_results],
    )


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
