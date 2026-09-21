from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.graph.workflow import quote_workflow
from app.models.approval import Approval
from app.schemas.workflow import (
    QuoteWorkflowResponse,
    WorkflowErrorResponse,
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
from app.services.agentops_service import (
    complete_workflow_run,
    create_workflow_run,
    fail_workflow_run,
    pause_workflow_run,
    record_workflow_event,
)


def create_quote_with_graph(
    message: str,
    db: Session,
    user_id: int,
    username: str,
    user_role: str,
    idempotency_key: str,
) -> QuoteWorkflowResponse:

    operation = "create_quote"

    scoped_key = build_scoped_key(
        user_id=user_id,
        operation=operation,
        idempotency_key=idempotency_key,
    )

    request_hash = build_request_hash(
        {
            "message": message,
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
                QuoteWorkflowResponse
                .model_validate(
                    cached_response
                )
            )

    record = create_idempotency_record(
        db=db,
        key=scoped_key,
        operation=operation,
        request_hash=request_hash,
    )

    thread_id = str(
        uuid4()
    )

    workflow_run = create_workflow_run(
        db=db,
        thread_id=thread_id,
        operation="create_quote",
        user_id=user_id,
        username=username,
        user_role=user_role,
    )

    record_workflow_event(
        db=db,
        workflow_run_id=workflow_run.id,
        event_type="workflow",
        status="started",
        message="Quote workflow started",
    )

    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    try:
        result = quote_workflow.invoke(
            {
                "message": message,
                "user_id": user_id,
                "username": username,
                "user_role": user_role,
                "workflow_run_id": workflow_run.id,
            },
            config=config,
        )

    except Exception:
        fail_idempotency_record(
            db=db,
            record=record,
        )

        raise

    quote = result.get(
        "quote"
    )

    if (
        result.get("workflow_status")
        == "failed"
    ):
        fail_workflow_run(
            db=db,
            workflow_run_id=workflow_run.id,
            error_type=result.get(
                "error_type"
            ),
            error_message=result.get(
                "error_message"
            ),
            retry_count=result.get(
                "retry_count"
            ),
        )

        record_workflow_event(
            db=db,
            workflow_run_id=workflow_run.id,
            event_type="workflow",
            status="failed",
            message=result.get(
                "error_message"
            ),
        )

        response = QuoteWorkflowResponse(
            thread_id=thread_id,
            status="failed",
            quote=quote,
            error=WorkflowErrorResponse(
                type=result.get(
                    "error_type",
                    "WorkflowError",
                ),
                message=result.get(
                    "error_message",
                    "Workflow failed",
                ),
                failed_node=result.get(
                    "failed_node"
                ),
                retry_count=result.get(
                    "retry_count"
                ),
            ),
        )

        complete_idempotency_record(
            db=db,
            record=record,
            response_data=response.model_dump(
                mode="json"
            ),
        )

        return response

    interrupts = result.get(
        "__interrupt__"
    )

    if interrupts:
        interrupt_value = (
            interrupts[0].value
        )

        pause_workflow_run(
            db=db,
            workflow_run_id=workflow_run.id,
        )

        approval = Approval(
            thread_id=thread_id,
            status="pending",
            requested_by_user_id=user_id,
        )

        db.add(approval)
        db.commit()

        response = QuoteWorkflowResponse(
            thread_id=thread_id,
            status="awaiting_approval",
            quote=quote,
            approval_request=interrupt_value,
        )

        complete_idempotency_record(
            db=db,
            record=record,
            response_data=response.model_dump(
                mode="json"
            ),
        )

        return response

    response = QuoteWorkflowResponse(
        thread_id=thread_id,
        status=result.get(
            "workflow_status",
            "ready",
        ),
        quote=quote,
    )

    complete_workflow_run(
        db=db,
        workflow_run_id=workflow_run.id,
        status=response.status,
    )

    record_workflow_event(
        db=db,
        workflow_run_id=workflow_run.id,
        event_type="workflow",
        status=response.status,
        message="Quote workflow completed",
    )

    complete_idempotency_record(
        db=db,
        record=record,
        response_data=response.model_dump(
            mode="json"
        ),
    )

    return response