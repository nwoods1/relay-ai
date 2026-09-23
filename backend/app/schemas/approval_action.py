from typing import Any

from pydantic import BaseModel


class ApprovalActionResult(BaseModel):
    thread_id: str
    decision: str
    status: str

    comment: str | None = None

    workflow_result: (
        dict[str, Any]
        | None
    ) = None