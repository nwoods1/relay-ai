from uuid import uuid4

from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.agent_intent import (
    AgentIntent,
)
from app.schemas.workflow import (
    QuoteWorkflowResponse,
)
from app.services.graph_quote_service import (
    create_quote_with_graph,
)


def build_normalized_quote_message(
    intent: AgentIntent,
    original_message: str,
) -> str:

    if (
        intent.customer_name
        and intent.product_name
        and intent.quantity is not None
    ):
        return (
            f"{intent.customer_name} wants "
            f"{intent.quantity} "
            f"{intent.product_name}."
        )

    return original_message


def run_quote_agent(
    db: Session,
    user: User,
    message: str,
    intent: AgentIntent,
    idempotency_key: str | None = None,
) -> QuoteWorkflowResponse:

    normalized_message = (
        build_normalized_quote_message(
            intent=intent,
            original_message=message,
        )
    )

    return create_quote_with_graph(
        message=normalized_message,
        db=db,
        user_id=user.id,
        username=user.username,
        user_role=user.role,
        idempotency_key=(
            idempotency_key
            or str(uuid4())
        ),
        create_approval_record=False,
    )