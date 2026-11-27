# ADR 0005: Upload intake and file storage

- Status: accepted
- Date: 2026-11-27
- Task: 1.2

## Context

`POST /submissions` accepts a client's manifest. The file must be kept exactly as received (validation results are tied to its SHA-256 hash), it must not be stored in the repository, and a database row and a file on disk have to stay consistent although they cannot be written in one transaction.

## Decisions

**Files on local disk, named by content hash.** `<UPLOAD_DIR>/<sha256>.csv`. The client's filename is stored in the database for display and is never used to build a path, which removes path traversal as a concern. `UPLOAD_DIR` defaults to `~/.lifesciences-platform/uploads`; a relative value is refused, because it would resolve against the directory the server was started in.

**Order: insert, store, commit.** The row is flushed first, so the unique constraint on `content_hash` refuses a duplicate (also two simultaneous ones) before anything touches the disk. Then the file is written to a temporary name and renamed, so it is complete or absent. Then the transaction commits. If storing fails, the row is rolled back. If the commit fails, a file without a row remains; it is harmless, because it is named by its own hash and the next upload of the same bytes overwrites it.

**The door checks only what it can know without reading the file:** filename, extension, declared content type, size, metadata fields. An empty (0-byte) file is accepted as `SUBMITTED`; validation reports it as `EMPTY_FILE` (spec sections 6 and 9), so the client gets it in the same report as every other content problem.

**Intake logic is separate from HTTP.** `workflows/intake.py` raises typed errors with stable codes; `api/submissions.py` maps them to status codes. The Streamlit app or a command-line tool can reuse the rules.

**One database session per request**, from a FastAPI dependency that builds the engine on first use. `/health` works without a database, and tests replace the dependency to run inside a rolled-back transaction.

**Plain `def` route.** File and database calls are blocking; FastAPI runs a `def` route in a worker thread.

## Dependencies added

`python-multipart` (FastAPI needs it for file uploads and form fields), `email-validator` (used by Pydantic's `EmailStr`, instead of a hand-written email pattern).

## Trade-offs and known limitations

- Local disk means one machine and no replication. Object storage would replace `store_file` later.
- The web framework receives and spools the whole request before the size check runs. The limit bounds what is kept and held in memory, not what a client can send. A deployment needs a body-size limit in front of the app.
- The content type is what the client declares; it is not proof that the file is CSV. Validation reads the content.
- The hash is unique across all clients: a second client with identical bytes gets 409 and sees the other submission's id. Acceptable only while there is no authentication and all data is synthetic.
- The same file cannot be submitted again to correct a wrong form field.
- All zero-byte files share one hash, so only the first can be submitted.

## Not decided here

Authentication, retention and deletion of stored files, virus scanning, resumable uploads.
