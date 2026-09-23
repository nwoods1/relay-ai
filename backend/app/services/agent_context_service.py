from sqlalchemy.orm import Session

from app.models.conversation import (
    Conversation,
)
from app.schemas.agent_context import (
    AgentConversationContext,
)
from app.schemas.agent_intent import (
    AgentIntent,
)


def get_conversation_context(
    conversation: Conversation,
) -> AgentConversationContext:

    return AgentConversationContext(
        customer_name=(
            conversation.last_customer_name
        ),
        product_name=(
            conversation.last_product_name
        ),
        quantity=(
            conversation.last_quantity
        ),
        pending_action=(
            conversation.pending_action
        ),
        pending_thread_id=(
            conversation.pending_thread_id
        ),
    )


def update_conversation_context(
    db: Session,
    conversation: Conversation,
    customer_name: str | None = None,
    product_name: str | None = None,
    quantity: int | None = None,
):
    if customer_name is not None:
        conversation.last_customer_name = (
            customer_name
        )

    if product_name is not None:
        conversation.last_product_name = (
            product_name
        )

    if quantity is not None:
        conversation.last_quantity = (
            quantity
        )

    db.commit()
    db.refresh(conversation)


def clear_conversation_context(
    db: Session,
    conversation: Conversation,
):
    conversation.last_customer_name = None
    conversation.last_product_name = None
    conversation.last_quantity = None

    db.commit()
    db.refresh(conversation)

def resolve_intent_context(
    intent: AgentIntent,
    context: AgentConversationContext,
) -> AgentIntent:

    data = intent.model_dump()

    if (
        not data["customer_name"]
        and data[
            "reference_previous_customer"
        ]
    ):
        data["customer_name"] = (
            context.customer_name
        )

    if (
        not data["product_name"]
        and data[
            "reference_previous_product"
        ]
    ):
        data["product_name"] = (
            context.product_name
        )

    if (
        data["quantity"] is None
        and data[
            "reference_previous_quantity"
        ]
    ):
        data["quantity"] = (
            context.quantity
        )

    return AgentIntent.model_validate(
        data
    )