import hashlib
import json

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.idempotency import IdempotencyRecord


def build_request_hash(
    payload: dict,
) -> str:
    normalized = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
    )

    return hashlib.sha256(
        normalized.encode("utf-8")
    ).hexdigest()


def build_scoped_key(
    user_id: int,
    operation: str,
    idempotency_key: str,
) -> str:
    return (
        f"user:{user_id}:"
        f"{operation}:"
        f"{idempotency_key}"
    )


def get_idempotency_record(
    db: Session,
    key: str,
    operation: str,
) -> IdempotencyRecord | None:
    return (
        db.query(IdempotencyRecord)
        .filter(
            IdempotencyRecord.key == key,
            IdempotencyRecord.operation
            == operation,
        )
        .first()
    )


def create_idempotency_record(
    db: Session,
    key: str,
    operation: str,
    request_hash: str,
) -> IdempotencyRecord:
    record = IdempotencyRecord(
        key=key,
        operation=operation,
        request_hash=request_hash,
        status="in_progress",
    )

    try:
        db.add(record)
        db.commit()
        db.refresh(record)

    except IntegrityError as exc:
        db.rollback()

        raise HTTPException(
            status_code=409,
            detail=(
                "A request with this "
                "idempotency key is already "
                "being processed"
            ),
        ) from exc

    return record


def validate_idempotency_request(
    record: IdempotencyRecord,
    request_hash: str,
):
    if (
        record.request_hash
        != request_hash
    ):
        raise HTTPException(
            status_code=409,
            detail=(
                "Idempotency key was already "
                "used with a different request"
            ),
        )


def complete_idempotency_record(
    db: Session,
    record: IdempotencyRecord,
    response_data: dict,
):
    record.status = "completed"

    record.response_json = json.dumps(
        response_data
    )

    db.commit()


def fail_idempotency_record(
    db: Session,
    record: IdempotencyRecord,
):
    record.status = "failed"

    db.commit()


def get_cached_response(
    record: IdempotencyRecord,
) -> dict | None:
    if (
        record.status == "completed"
        and record.response_json
    ):
        return json.loads(
            record.response_json
        )

    return None


def handle_existing_record(
    record: IdempotencyRecord,
    request_hash: str,
) -> dict | None:
    validate_idempotency_request(
        record,
        request_hash,
    )

    cached_response = get_cached_response(
        record
    )

    if cached_response:
        return cached_response

    if record.status == "in_progress":
        raise HTTPException(
            status_code=409,
            detail=(
                "A request with this "
                "idempotency key is already "
                "in progress"
            ),
        )

    if record.status == "failed":
        raise HTTPException(
            status_code=409,
            detail=(
                "Previous request with this "
                "idempotency key failed. "
                "Retry with a new key."
            ),
        )

    return None