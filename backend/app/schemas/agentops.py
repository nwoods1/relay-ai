from datetime import datetime

from pydantic import BaseModel


class WorkflowRunSummary(BaseModel):
    thread_id: str
    operation: str
    username: str
    user_role: str
    status: str
    current_node: str | None
    requires_approval: bool
    total_tokens: int
    duration_ms: float | None
    started_at: datetime
    completed_at: datetime | None


class WorkflowEventResponse(BaseModel):
    id: int
    event_type: str
    node_name: str | None
    status: str
    message: str | None
    metadata: dict | None = None
    created_at: datetime

class WorkflowRunDetail(
    WorkflowRunSummary
):
    error_type: str | None
    error_message: str | None
    retry_count: int

    input_tokens: int
    output_tokens: int
    llm_latency_ms: float | None

    events: list[
        WorkflowEventResponse
    ]


class AgentOpsSummary(BaseModel):
    total_runs: int
    ready_runs: int
    awaiting_approval_runs: int
    approved_runs: int
    rejected_runs: int
    failed_runs: int

    average_duration_ms: float | None
    total_tokens: int