from datetime import datetime

from fastapi import HTTPException
from langgraph.types import Command
from sqlalchemy.orm import Session

from app.graph.workflow import quote_workflow
from app.models.approval import Approval
from app.schemas.workflow import ApprovalDecisionResponse


def resume_quote_workflow(
    thread_id: str,
    decision: str,
    comment: str | None,
    user_id: int,
    username: str,
    db: Session,
) -> ApprovalDecisionResponse:

    # Find the business approval record
    approval = (
        db.query(Approval)
        .filter(
            Approval.thread_id == thread_id
        )
        .first()
    )

    if not approval:
        raise HTTPException(
            status_code=404,
            detail="Approval request not found",
        )

    # Prevent the same approval from being decided twice
    if approval.status != "pending":
        raise HTTPException(
            status_code=409,
            detail=(
                "Approval request has already "
                "been decided"
            ),
        )

    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    resume_payload = {
        "decision": decision,
        "comment": comment,
        "user_id": user_id,
        "username": username,
    }

    # Resume the suspended LangGraph workflow
    result = quote_workflow.invoke(
        Command(
            resume=resume_payload
        ),
        config=config,
    )

    # Update the business approval audit record
    approval.status = decision
    approval.decided_by_user_id = user_id
    approval.decision_comment = comment
    approval.decided_at = datetime.utcnow()

    db.commit()

    return ApprovalDecisionResponse(
        thread_id=thread_id,
        status=result["workflow_status"],
        quote=result.get("quote"),
    )