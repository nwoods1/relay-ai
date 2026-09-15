from langgraph.types import Command
from sqlalchemy.orm import Session
from uuid import uuid4

from app.graph.workflow import quote_workflow
from app.schemas.quote import QuoteResponse
from app.schemas.workflow import (
    QuoteWorkflowResponse,
    ApprovalDecisionResponse,
)
from app.models.approval import Approval

def create_quote_with_graph(
    message: str,
    db: Session,
    user_id: int,
    username: str,
    user_role: str,
) -> QuoteWorkflowResponse:

    thread_id = str(
        uuid4()
    )

    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    result = quote_workflow.invoke(
        {
            "message": message,
            "user_id": user_id,
            "username": username,
            "user_role": user_role,
        },
        config=config,
    )

    quote = result.get("quote")

    interrupts = result.get(
        "__interrupt__"
    )

    if interrupts:
        interrupt_value = (
            interrupts[0].value
        )
        approval = Approval(
            thread_id=thread_id,
            status="pending",
            requested_by_user_id=user_id,
        )

        db.add(approval)
        db.commit()

        return QuoteWorkflowResponse(
            thread_id=thread_id,
            status="awaiting_approval",
            quote=quote,
            approval_request=interrupt_value,
        )

    return QuoteWorkflowResponse(
        thread_id=thread_id,
        status=result.get(
            "workflow_status",
            "ready",
        ),
        quote=quote,
    )