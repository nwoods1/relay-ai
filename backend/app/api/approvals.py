from fastapi import (
    APIRouter,
    Depends,
    Header,
    HTTPException,
)
from sqlalchemy.orm import Session

from app.api.dependencies import require_permission
from app.core.database import get_db
from app.models.approval import Approval
from app.models.user import User
from app.schemas.workflow import (
    ApprovalDecisionRequest,
    ApprovalDecisionResponse,
    ApprovalStatusResponse,
    PendingApprovalResponse,
)
from app.services.approval_service import (
    resume_quote_workflow,
)


router = APIRouter(
    prefix="/approvals",
    tags=["Approvals"],
)


@router.post(
    "/{thread_id}",
    response_model=ApprovalDecisionResponse,
)
def decide_quote_approval(
    thread_id: str,
    request: ApprovalDecisionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("quote:approve")
    ),
    idempotency_key: str = Header(
        ...,
        alias="Idempotency-Key",
        min_length=8,
        max_length=255,
    ),
):
    return resume_quote_workflow(
        thread_id=thread_id,
        decision=request.decision,
        comment=request.comment,
        user_id=current_user.id,
        username=current_user.username,
        db=db,
        idempotency_key=idempotency_key,
    )


@router.get(
    "/",
    response_model=list[
        PendingApprovalResponse
    ],
)
def get_pending_approvals(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("quote:approve")
    ),
):
    return (
        db.query(Approval)
        .filter(
            Approval.status == "pending"
        )
        .order_by(
            Approval.created_at.desc()
        )
        .all()
    )


@router.get(
    "/{thread_id}",
    response_model=ApprovalStatusResponse,
)
def get_approval_status(
    thread_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("quote:approve")
    ),
):
    approval = (
        db.query(Approval)
        .filter(
            Approval.thread_id
            == thread_id
        )
        .first()
    )

    if not approval:
        raise HTTPException(
            status_code=404,
            detail="Approval request not found",
        )

    return approval