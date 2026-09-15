from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel

from app.schemas.quote import QuoteResponse


class PendingApprovalResponse(BaseModel):
    thread_id: str
    status: str
    requested_by_user_id: int
    created_at: datetime


class QuoteWorkflowResponse(BaseModel):
    thread_id: str
    status: str
    quote: QuoteResponse | None = None
    approval_request: dict[str, Any] | None = None


class ApprovalDecisionRequest(BaseModel):
    decision: Literal[
        "approved",
        "rejected",
    ]
    comment: str | None = None


class ApprovalDecisionResponse(BaseModel):
    thread_id: str
    status: str
    quote: QuoteResponse | None = None


class ApprovalStatusResponse(BaseModel):
    thread_id: str
    status: str
    requested_by_user_id: int
    decided_by_user_id: int | None
    decision_comment: str | None
    created_at: datetime
    decided_at: datetime | None