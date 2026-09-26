from types import SimpleNamespace

from app.schemas.agent_context import (
    AgentConversationContext,
)
from app.schemas.agent_intent import (
    AgentIntent,
)
from app.services.agent_context_service import (
    build_router_input,
    resolve_intent_context,
    update_conversation_context,
)


class FakeDB:
    def commit(
        self,
    ):
        pass

    def refresh(
        self,
        obj,
    ):
        pass


def make_conversation():
    return SimpleNamespace(
        last_customer_name=None,
        last_product_name=None,
        last_quantity=None,
        last_warehouse_name=None,
        last_approval_thread_id=None,
        last_approval_action=None,
        recent_customers=[],
        recent_products=[],
        recent_quantities=[],
        recent_warehouses=[],
        recent_actions=[],
        conversation_summary=None,
    )


def test_recent_products_keep_multiple_values():
    db = FakeDB()

    conversation = (
        make_conversation()
    )

    update_conversation_context(
        db=db,
        conversation=conversation,
        product_name=(
            "Alpine Shell Jacket"
        ),
        action="check_inventory",
    )

    update_conversation_context(
        db=db,
        conversation=conversation,
        product_name=(
            "Merino Wool Toque"
        ),
        action="check_inventory",
    )

    assert (
        conversation.recent_products
        == [
            "Merino Wool Toque",
            "Alpine Shell Jacket",
        ]
    )


def test_duplicate_product_moves_to_front():
    db = FakeDB()

    conversation = (
        make_conversation()
    )

    update_conversation_context(
        db=db,
        conversation=conversation,
        product_name=(
            "Alpine Shell Jacket"
        ),
    )

    update_conversation_context(
        db=db,
        conversation=conversation,
        product_name=(
            "Merino Wool Toque"
        ),
    )

    update_conversation_context(
        db=db,
        conversation=conversation,
        product_name=(
            "Alpine Shell Jacket"
        ),
    )

    assert (
        conversation.recent_products
        == [
            "Alpine Shell Jacket",
            "Merino Wool Toque",
        ]
    )


def test_previous_product_reference():
    context = (
        AgentConversationContext(
            product_name=(
                "Merino Wool Toque"
            ),
            recent_products=[
                "Merino Wool Toque",
                "Alpine Shell Jacket",
            ],
        )
    )

    intent = AgentIntent(
        intent="check_inventory",
        reference_previous_product=True,
    )

    resolved = (
        resolve_intent_context(
            intent=intent,
            context=context,
        )
    )

    assert (
        resolved.product_name
        == "Merino Wool Toque"
    )


def test_other_product_reference():
    context = (
        AgentConversationContext(
            product_name=(
                "Merino Wool Toque"
            ),
            recent_products=[
                "Merino Wool Toque",
                "Alpine Shell Jacket",
            ],
        )
    )

    intent = AgentIntent(
        intent="check_inventory",
        reference_other_product=True,
    )

    resolved = (
        resolve_intent_context(
            intent=intent,
            context=context,
        )
    )

    assert (
        resolved.product_name
        == "Alpine Shell Jacket"
    )


def test_quote_quantity_change_uses_previous_context():
    context = (
        AgentConversationContext(
            customer_name=(
                "Pacific Mountain Outfitters"
            ),
            product_name=(
                "Merino Wool Toque"
            ),
            quantity=20,
            recent_customers=[
                "Pacific Mountain Outfitters"
            ],
            recent_products=[
                "Merino Wool Toque"
            ],
            recent_quantities=[
                20
            ],
        )
    )

    intent = AgentIntent(
        intent="create_quote",
        quantity=15,
        reference_previous_customer=True,
        reference_previous_product=True,
    )

    resolved = (
        resolve_intent_context(
            intent=intent,
            context=context,
        )
    )

    assert (
        resolved.customer_name
        == "Pacific Mountain Outfitters"
    )

    assert (
        resolved.product_name
        == "Merino Wool Toque"
    )

    assert resolved.quantity == 15


def test_summary_contains_recent_context():
    db = FakeDB()

    conversation = (
        make_conversation()
    )

    update_conversation_context(
        db=db,
        conversation=conversation,
        customer_name=(
            "Pacific Mountain Outfitters"
        ),
        product_name=(
            "Alpine Shell Jacket"
        ),
        quantity=30,
        action="create_quote",
    )

    assert (
        "Pacific Mountain Outfitters"
        in conversation
        .conversation_summary
    )

    assert (
        "Alpine Shell Jacket"
        in conversation
        .conversation_summary
    )

    assert (
        "create_quote"
        in conversation
        .conversation_summary
    )


def test_router_input_separates_memory_from_user_message():
    context = (
        AgentConversationContext(
            conversation_summary=(
                "Recent products: "
                "Alpine Shell Jacket."
            )
        )
    )

    result = build_router_input(
        context=context,
        user_message=(
            "How many of those "
            "are available?"
        ),
    )

    assert (
        "<conversation_context>"
        in result
    )

    assert (
        "<current_user_message>"
        in result
    )

    assert (
        "Alpine Shell Jacket"
        in result
    )