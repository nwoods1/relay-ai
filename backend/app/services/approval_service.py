from datetime import datetime

from fastapi import HTTPException
from langgraph.types import Command
from sqlalchemy.orm import Session

from app.graph.workflow import quote_workflow
from app.models.approval import Approval
from app.models.workflow_run import WorkflowRun
from app.schemas.workflow import (
    ApprovalDecisionResponse,
)
from app.services.agentops_service import (
    complete_workflow_run,
    record_workflow_event,
)
from app.services.idempotency_service import (
    build_request_hash,
    build_scoped_key,
    complete_idempotency_record,
    create_idempotency_record,
    fail_idempotency_record,
    get_idempotency_record,
    handle_existing_record,
)


def resume_quote_workflow(
    thread_id: str,
    decision: str,
    comment: str | None,
    user_id: int,
    username: str,
    db: Session,
    idempotency_key: str,
) -> ApprovalDecisionResponse:

    operation = "approve_quote"

    scoped_key = build_scoped_key(
        user_id=user_id,
        operation=operation,
        idempotency_key=idempotency_key,
    )

    request_hash = build_request_hash(
        {
            "thread_id": thread_id,
            "decision": decision,
            "comment": comment,
            "user_id": user_id,
        }
    )

    existing_record = get_idempotency_record(
        db=db,
        key=scoped_key,
        operation=operation,
    )

    if existing_record:
        cached_response = handle_existing_record(
            existing_record,
            request_hash,
        )

        if cached_response:
            return (
                ApprovalDecisionResponse
                .model_validate(
                    cached_response
                )
            )

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

    if approval.status != "pending":
        raise HTTPException(
            status_code=409,
            detail=(
                "Approval request has already "
                "been decided"
            ),
        )

    workflow_run = (
        db.query(WorkflowRun)
        .filter(
            WorkflowRun.thread_id
            == thread_id
        )
        .first()
    )

    record = create_idempotency_record(
        db=db,
        key=scoped_key,
        operation=operation,
        request_hash=request_hash,
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

    snapshot = quote_workflow.get_state(
        config
    )

    if (
        snapshot is None
        or not snapshot.values
    ):
        raise HTTPException(
            status_code=409,
            detail=(
                "The workflow checkpoint for "
                "this approval no longer exists. "
                "The approval request is stale."
            ),
        )

    try:
        result = quote_workflow.invoke(
            Command(
                resume=resume_payload
            ),
            config=config,
        )

    except Exception:
        fail_idempotency_record(
            db=db,
            record=record,
        )

        raise

    approval.status = decision
    approval.decided_by_user_id = user_id
    approval.decision_comment = comment
    approval.decided_at = datetime.utcnow()

    db.commit()

    if workflow_run:
        complete_workflow_run(
            db=db,
            workflow_run_id=workflow_run.id,
            status=decision,
            requires_approval=True,
        )

        record_workflow_event(
            db=db,
            workflow_run_id=workflow_run.id,
            event_type="approval",
            status=decision,
            message=comment,
            metadata={
                "decided_by_user_id":
                    user_id,
                "decided_by_username":
                    username,
            },
        )

    response = ApprovalDecisionResponse(
        thread_id=thread_id,
        status=result["workflow_status"],
        quote=result.get("quote"),
    )

    complete_idempotency_record(
        db=db,
        record=record,
        response_data=response.model_dump(
            mode="json"
        ),
    )

    return response