import json

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.dependencies import (
    require_permission,
)
from app.core.database import get_db
from app.models.user import User
from app.models.workflow_event import (
    WorkflowEvent,
)
from app.models.workflow_run import (
    WorkflowRun,
)
from app.schemas.agentops import (
    AgentOpsSummary,
    WorkflowEventResponse,
    WorkflowRunDetail,
    WorkflowRunSummary,
)


router = APIRouter(
    prefix="/agentops",
    tags=["AgentOps"],
)

@router.get(
    "/runs",
    response_model=list[
        WorkflowRunSummary
    ],
)
def list_workflow_runs(
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(
            "monitoring:read"
        )
    ),
):
    runs = (
        db.query(WorkflowRun)
        .order_by(
            WorkflowRun.started_at.desc()
        )
        .limit(min(limit, 100))
        .all()
    )

    return runs

@router.get(
    "/runs/{thread_id}",
    response_model=WorkflowRunDetail,
)
def get_workflow_run(
    thread_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(
            "monitoring:read"
        )
    ),
):
    run = (
        db.query(WorkflowRun)
        .filter(
            WorkflowRun.thread_id
            == thread_id
        )
        .first()
    )

    if not run:
        raise HTTPException(
            status_code=404,
            detail="Workflow run not found",
        )

    events = (
        db.query(WorkflowEvent)
        .filter(
            WorkflowEvent.workflow_run_id
            == run.id
        )
        .order_by(
            WorkflowEvent.created_at.asc()
        )
        .all()
    )

    return WorkflowRunDetail(
        thread_id=run.thread_id,
        operation=run.operation,
        username=run.username,
        user_role=run.user_role,
        status=run.status,
        current_node=run.current_node,
        requires_approval=
            run.requires_approval,
        total_tokens=run.total_tokens,
        duration_ms=run.duration_ms,
        started_at=run.started_at,
        completed_at=run.completed_at,
        error_type=run.error_type,
        error_message=
            run.error_message,
        retry_count=run.retry_count,
        input_tokens=run.input_tokens,
        output_tokens=run.output_tokens,
        llm_latency_ms=
            run.llm_latency_ms,
        events=[
            WorkflowEventResponse(
                id=event.id,
                event_type=
                    event.event_type,
                node_name=
                    event.node_name,
                status=event.status,
                message=event.message,
                created_at=
                    event.created_at,
            )
            for event in events
        ],
    )

@router.get(
    "/summary",
    response_model=AgentOpsSummary,
)
def get_agentops_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(
            "monitoring:read"
        )
    ),
):
    total_runs = (
        db.query(func.count(WorkflowRun.id))
        .scalar()
        or 0
    )

    def count_status(
        status: str,
    ) -> int:
        return (
            db.query(
                func.count(WorkflowRun.id)
            )
            .filter(
                WorkflowRun.status
                == status
            )
            .scalar()
            or 0
        )

    average_duration = (
        db.query(
            func.avg(
                WorkflowRun.duration_ms
            )
        )
        .filter(
            WorkflowRun.duration_ms
            .isnot(None)
        )
        .scalar()
    )

    total_tokens = (
        db.query(
            func.sum(
                WorkflowRun.total_tokens
            )
        )
        .scalar()
        or 0
    )

    return AgentOpsSummary(
        total_runs=total_runs,
        ready_runs=count_status(
            "ready"
        ),
        awaiting_approval_runs=
            count_status(
                "awaiting_approval"
            ),
        approved_runs=count_status(
            "approved"
        ),
        rejected_runs=count_status(
            "rejected"
        ),
        failed_runs=count_status(
            "failed"
        ),
        average_duration_ms=(
            float(average_duration)
            if average_duration
            is not None
            else None
        ),
        total_tokens=total_tokens,
    )