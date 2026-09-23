from uuid import uuid4

from sqlalchemy.orm import Session

from app.models.approval import Approval
from app.models.user import User
from app.schemas.workflow import (
    ApprovalDecisionResponse,
)
from app.services.approval_service import (
    resume_quote_workflow,
)


def list_pending_approvals(
    db: Session,
) -> list[Approval]:

    return (
        db.query(Approval)
        .filter(
            Approval.status == "pending"
        )
        .order_by(
            Approval.created_at.asc()
        )
        .all()
    )


def get_approval_by_thread(
    db: Session,
    thread_id: str,
) -> Approval | None:

    return (
        db.query(Approval)
        .filter(
            Approval.thread_id == thread_id
        )
        .first()
    )


def get_pending_approval(
    db: Session,
    thread_id: str,
) -> Approval | None:

    return (
        db.query(Approval)
        .filter(
            Approval.thread_id == thread_id,
            Approval.status == "pending",
        )
        .first()
    )


def count_pending_approvals(
    db: Session,
) -> int:

    return (
        db.query(Approval)
        .filter(
            Approval.status == "pending"
        )
        .count()
    )


def approve_pending_approval(
    db: Session,
    thread_id: str,
    user: User,
    comment: str | None = None,
    idempotency_key: str | None = None,
) -> ApprovalDecisionResponse:

    return resume_quote_workflow(
        thread_id=thread_id,
        decision="approved",
        comment=comment,
        user_id=user.id,
        username=user.username,
        db=db,
        idempotency_key=(
            idempotency_key
            or str(uuid4())
        ),
    )


def reject_pending_approval(
    db: Session,
    thread_id: str,
    user: User,
    comment: str | None = None,
    idempotency_key: str | None = None,
) -> ApprovalDecisionResponse:

    return resume_quote_workflow(
        thread_id=thread_id,
        decision="rejected",
        comment=comment,
        user_id=user.id,
        username=user.username,
        db=db,
        idempotency_key=(
            idempotency_key
            or str(uuid4())
        ),
    )