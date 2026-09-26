from datetime import datetime
from typing import Any

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


MAX_RECENT_ENTITIES = 5
MAX_RECENT_ACTIONS = 8


def _remember_string(
    existing: list | None,
    value: str,
    limit: int = MAX_RECENT_ENTITIES,
) -> list[str]:

    current = list(
        existing or []
    )

    normalized = (
        value.strip().lower()
    )

    filtered = [
        item
        for item in current
        if (
            isinstance(
                item,
                str,
            )
            and item.strip().lower()
            != normalized
        )
    ]

    return [
        value.strip(),
        *filtered,
    ][:limit]


def _remember_number(
    existing: list | None,
    value: int,
    limit: int = MAX_RECENT_ENTITIES,
) -> list[int]:

    current = list(
        existing or []
    )

    filtered = [
        item
        for item in current
        if item != value
    ]

    return [
        value,
        *filtered,
    ][:limit]


def _record_action(
    conversation: Conversation,
    action: str,
    details: dict[str, Any] | None = None,
) -> None:

    existing = list(
        conversation.recent_actions
        or []
    )

    item = {
        "action": action,
        "details": details or {},
        "timestamp": (
            datetime.utcnow()
            .isoformat()
        ),
    }

    conversation.recent_actions = [
        item,
        *existing,
    ][:MAX_RECENT_ACTIONS]


def _refresh_summary(
    conversation: Conversation,
) -> None:

    parts: list[str] = []

    customers = (
        conversation.recent_customers
        or []
    )

    products = (
        conversation.recent_products
        or []
    )

    quantities = (
        conversation.recent_quantities
        or []
    )

    warehouses = (
        conversation.recent_warehouses
        or []
    )

    actions = (
        conversation.recent_actions
        or []
    )

    if customers:
        parts.append(
            "Recent customers: "
            + ", ".join(
                customers[:3]
            )
            + "."
        )

    if products:
        parts.append(
            "Recent products: "
            + ", ".join(
                products[:3]
            )
            + "."
        )

    if quantities:
        parts.append(
            "Recent quantities: "
            + ", ".join(
                str(value)
                for value
                in quantities[:3]
            )
            + "."
        )

    if warehouses:
        parts.append(
            "Recent warehouses: "
            + ", ".join(
                warehouses[:3]
            )
            + "."
        )

    if actions:
        action_names = [
            item.get(
                "action",
                "unknown",
            )
            for item
            in actions[:4]
        ]

        parts.append(
            "Recent actions: "
            + ", ".join(
                action_names
            )
            + "."
        )

    if (
        conversation
        .last_approval_thread_id
    ):
        parts.append(
            "Current approval thread: "
            + conversation
            .last_approval_thread_id
            + "."
        )

    conversation.conversation_summary = (
        " ".join(parts)
        if parts
        else None
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
        warehouse_name=(
            conversation.last_warehouse_name
        ),
        pending_action=(
            conversation.pending_action
        ),
        pending_thread_id=(
            conversation.pending_thread_id
        ),
        last_approval_thread_id=(
            conversation
            .last_approval_thread_id
        ),
        last_approval_action=(
            conversation
            .last_approval_action
        ),
        recent_customers=list(
            conversation.recent_customers
            or []
        ),
        recent_products=list(
            conversation.recent_products
            or []
        ),
        recent_quantities=list(
            conversation.recent_quantities
            or []
        ),
        recent_warehouses=list(
            conversation.recent_warehouses
            or []
        ),
        recent_actions=list(
            conversation.recent_actions
            or []
        ),
        conversation_summary=(
            conversation
            .conversation_summary
        ),
    )


def update_conversation_context(
    db: Session,
    conversation: Conversation,
    customer_name: str | None = None,
    product_name: str | None = None,
    quantity: int | None = None,
    warehouse_name: str | None = None,
    action: str | None = None,
    action_details: (
        dict[str, Any]
        | None
    ) = None,
) -> None:

    if customer_name is not None:
        customer_name = (
            customer_name.strip()
        )

        conversation.last_customer_name = (
            customer_name
        )

        conversation.recent_customers = (
            _remember_string(
                conversation.recent_customers,
                customer_name,
            )
        )

    if product_name is not None:
        product_name = (
            product_name.strip()
        )

        conversation.last_product_name = (
            product_name
        )

        conversation.recent_products = (
            _remember_string(
                conversation.recent_products,
                product_name,
            )
        )

    if quantity is not None:
        conversation.last_quantity = (
            quantity
        )

        conversation.recent_quantities = (
            _remember_number(
                conversation.recent_quantities,
                quantity,
            )
        )

    if warehouse_name is not None:
        warehouse_name = (
            warehouse_name.strip()
        )

        conversation.last_warehouse_name = (
            warehouse_name
        )

        conversation.recent_warehouses = (
            _remember_string(
                conversation.recent_warehouses,
                warehouse_name,
            )
        )

    if action is not None:
        _record_action(
            conversation=conversation,
            action=action,
            details=action_details,
        )

    _refresh_summary(
        conversation
    )

    db.commit()

    db.refresh(
        conversation
    )


def clear_conversation_context(
    db: Session,
    conversation: Conversation,
) -> None:

    conversation.last_customer_name = None
    conversation.last_product_name = None
    conversation.last_quantity = None
    conversation.last_warehouse_name = None

    conversation.recent_customers = []
    conversation.recent_products = []
    conversation.recent_quantities = []
    conversation.recent_warehouses = []
    conversation.recent_actions = []

    conversation.conversation_summary = None

    db.commit()

    db.refresh(
        conversation
    )


def record_conversation_action(
    db: Session,
    conversation: Conversation,
    action: str,
    details: (
        dict[str, Any]
        | None
    ) = None,
) -> None:

    _record_action(
        conversation=conversation,
        action=action,
        details=details,
    )

    _refresh_summary(
        conversation
    )

    db.commit()

    db.refresh(
        conversation
    )


def update_approval_context(
    db: Session,
    conversation: Conversation,
    thread_id: str | None = None,
    action: str | None = None,
) -> None:

    if thread_id is not None:
        conversation.last_approval_thread_id = (
            thread_id
        )

    if action is not None:
        conversation.last_approval_action = (
            action
        )

        _record_action(
            conversation=conversation,
            action=(
                f"approval_{action}"
            ),
            details={
                "thread_id":
                    thread_id
                    or conversation
                    .last_approval_thread_id
            },
        )

    _refresh_summary(
        conversation
    )

    db.commit()

    db.refresh(
        conversation
    )


def clear_approval_context(
    db: Session,
    conversation: Conversation,
    action: str | None = None,
) -> None:

    old_thread_id = (
        conversation
        .last_approval_thread_id
    )

    conversation.last_approval_thread_id = (
        None
    )

    if action is not None:
        conversation.last_approval_action = (
            action
        )

        _record_action(
            conversation=conversation,
            action=(
                f"approval_{action}"
            ),
            details={
                "thread_id":
                    old_thread_id
            },
        )

    _refresh_summary(
        conversation
    )

    db.commit()

    db.refresh(
        conversation
    )


def resolve_intent_context(
    intent: AgentIntent,
    context: AgentConversationContext,
) -> AgentIntent:

    data = intent.model_dump()

    # ----------------------------------
    # Customer references
    # ----------------------------------

    if (
        not data["customer_name"]
        and data[
            "reference_previous_customer"
        ]
    ):
        data["customer_name"] = (
            context.customer_name
            or (
                context.recent_customers[0]
                if context.recent_customers
                else None
            )
        )

    if (
        not data["customer_name"]
        and data[
            "reference_other_customer"
        ]
        and len(
            context.recent_customers
        ) > 1
    ):
        data["customer_name"] = (
            context.recent_customers[1]
        )

    # ----------------------------------
    # Product references
    # ----------------------------------

    if (
        not data["product_name"]
        and data[
            "reference_previous_product"
        ]
    ):
        data["product_name"] = (
            context.product_name
            or (
                context.recent_products[0]
                if context.recent_products
                else None
            )
        )

    if (
        not data["product_name"]
        and data[
            "reference_other_product"
        ]
        and len(
            context.recent_products
        ) > 1
    ):
        data["product_name"] = (
            context.recent_products[1]
        )

    # ----------------------------------
    # Quantity references
    # ----------------------------------

    if (
        data["quantity"] is None
        and data[
            "reference_previous_quantity"
        ]
    ):
        data["quantity"] = (
            context.quantity
            if context.quantity
            is not None
            else (
                context.recent_quantities[0]
                if context.recent_quantities
                else None
            )
        )

    # ----------------------------------
    # Warehouse references
    # ----------------------------------

    if (
        not data["warehouse_name"]
        and data[
            "reference_previous_warehouse"
        ]
    ):
        data["warehouse_name"] = (
            context.warehouse_name
            or (
                context
                .recent_warehouses[0]
                if (
                    context
                    .recent_warehouses
                )
                else None
            )
        )

    if (
        not data["warehouse_name"]
        and data[
            "reference_other_warehouse"
        ]
        and len(
            context.recent_warehouses
        ) > 1
    ):
        data["warehouse_name"] = (
            context.recent_warehouses[1]
        )

    # ----------------------------------
    # Approval references
    # ----------------------------------

    if (
        not data["approval_thread_id"]
        and data[
            "reference_previous_approval"
        ]
    ):
        data["approval_thread_id"] = (
            context
            .last_approval_thread_id
        )

    return AgentIntent.model_validate(
        data
    )


def build_router_input(
    context: AgentConversationContext,
    user_message: str,
) -> str:

    summary = (
        context.conversation_summary
        or "No prior conversation memory."
    )

    return (
        "<conversation_context>\n"
        f"{summary}\n"
        "</conversation_context>\n\n"
        "<current_user_message>\n"
        f"{user_message}\n"
        "</current_user_message>"
    )