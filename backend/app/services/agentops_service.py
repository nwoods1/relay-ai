import json
from datetime import datetime

from sqlalchemy.orm import Session

from app.models.workflow_event import WorkflowEvent
from app.models.workflow_run import WorkflowRun


def create_workflow_run(
    db: Session,
    thread_id: str,
    operation: str,
    user_id: int,
    username: str,
    user_role: str,
) -> WorkflowRun:

    run = WorkflowRun(
        thread_id=thread_id,
        operation=operation,
        user_id=user_id,
        username=username,
        user_role=user_role,
        status="running",
    )

    db.add(run)
    db.commit()
    db.refresh(run)

    return run


def record_workflow_event(
    db: Session,
    workflow_run_id: int,
    event_type: str,
    status: str,
    node_name: str | None = None,
    message: str | None = None,
    metadata: dict | None = None,
):
    event = WorkflowEvent(
        workflow_run_id=workflow_run_id,
        event_type=event_type,
        node_name=node_name,
        status=status,
        message=message,
        metadata_json=(
            json.dumps(metadata)
            if metadata
            else None
        ),
    )

    db.add(event)
    db.commit()


def update_current_node(
    db: Session,
    workflow_run_id: int,
    node_name: str,
):
    run = db.get(
        WorkflowRun,
        workflow_run_id,
    )

    if not run:
        return

    run.current_node = node_name

    db.commit()


def complete_workflow_run(
    db: Session,
    workflow_run_id: int,
    status: str,
    requires_approval: bool = False,
):
    run = db.get(
        WorkflowRun,
        workflow_run_id,
    )

    if not run:
        return

    completed_at = datetime.utcnow()

    run.status = status
    run.requires_approval = requires_approval
    run.completed_at = completed_at

    run.duration_ms = (
        completed_at - run.started_at
    ).total_seconds() * 1000

    db.commit()


def fail_workflow_run(
    db: Session,
    workflow_run_id: int,
    error_type: str | None,
    error_message: str | None,
    retry_count: int | None,
):
    run = db.get(
        WorkflowRun,
        workflow_run_id,
    )

    if not run:
        return

    completed_at = datetime.utcnow()

    run.status = "failed"
    run.error_type = error_type
    run.error_message = error_message
    run.retry_count = retry_count or 0
    run.completed_at = completed_at

    run.duration_ms = (
        completed_at - run.started_at
    ).total_seconds() * 1000

    db.commit()


def record_llm_metrics(
    db: Session,
    workflow_run_id: int,
    input_tokens: int,
    output_tokens: int,
    total_tokens: int,
    latency_ms: float | None,
):
    run = db.get(
        WorkflowRun,
        workflow_run_id,
    )

    if not run:
        return

    run.input_tokens += input_tokens
    run.output_tokens += output_tokens
    run.total_tokens += total_tokens

    if latency_ms is not None:
        run.llm_latency_ms = latency_ms

    db.commit()

def pause_workflow_run(
    db: Session,
    workflow_run_id: int,
):
    run = db.get(
        WorkflowRun,
        workflow_run_id,
    )

    if not run:
        return

    run.status = "awaiting_approval"
    run.requires_approval = True

    db.commit()