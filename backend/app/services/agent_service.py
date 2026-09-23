from uuid import uuid4

from sqlalchemy.orm import Session

from app.agents.approval_agent import (
    list_pending_approvals,
)
from app.agents.general_agent import (
    run_general_agent,
)
from app.agents.inventory_agent import (
    run_inventory_agent,
)
from app.agents.quote_agent import (
    run_quote_agent,
)
from app.agents.router import (
    select_agent,
)
from app.llm.agent_router import (
    parse_agent_intent,
)
from app.models.approval import Approval
from app.models.user import User
from app.monitoring.logger import logger
from app.schemas.agent import (
    AgentAction,
    AgentChatRequest,
    AgentChatResponse,
)
from app.services.agent_context_service import (
    get_conversation_context,
    resolve_intent_context,
    update_conversation_context,
)
from app.services.conversation_service import (
    add_message,
    clear_pending_action,
    get_or_create_conversation,
    set_pending_action,
)


YES_MESSAGES = {
    "yes",
    "yes please",
    "yeah",
    "yep",
    "sure",
    "do it",
    "go ahead",
    "submit it",
    "please do",
}

NO_MESSAGES = {
    "no",
    "no thanks",
    "cancel",
    "don't",
    "dont",
    "never mind",
    "nevermind",
}


def build_quote_response(
    result,
) -> str:

    quote = result.quote

    if not quote:
        return (
            "I couldn't create the quote."
        )

    message = (
        f"I found {quote.customer_name} "
        f"and checked current inventory.\n\n"
        f"{quote.quantity_requested} "
        f"{quote.product_name} can be fulfilled "
        f"at ${quote.unit_price:,.2f} each, "
        f"for a subtotal of "
        f"${quote.subtotal:,.2f}."
    )

    if (
        result.status
        == "awaiting_approval"
    ):
        message += (
            "\n\nThis quote requires "
            "manager approval."
        )

        if quote.approval_reasons:
            message += (
                "\n\nReason: "
                + "; ".join(
                    quote.approval_reasons
                )
            )

        message += (
            "\n\nWould you like me to "
            "submit it for approval?"
        )

    else:
        message += (
            "\n\nThe quote is ready."
        )

    return message


def extract_sellable_quantity(
    inventory,
) -> int:

    if isinstance(
        inventory,
        (int, float),
    ):
        return int(
            inventory
        )

    if isinstance(
        inventory,
        list,
    ):
        return sum(
            extract_sellable_quantity(
                item
            )
            for item in inventory
        )

    if not isinstance(
        inventory,
        dict,
    ):
        return 0

    direct_fields = [
        "total_sellable",
        "sellable_quantity",
        "quantity_sellable",
        "total_available",
        "quantity_available",
        "available_quantity",
        "sellable",
    ]

    for field in direct_fields:
        value = inventory.get(
            field
        )

        if isinstance(
            value,
            (int, float),
        ):
            return int(
                value
            )

    collection_fields = [
        "warehouses",
        "inventory",
        "locations",
        "records",
        "items",
    ]

    for field in collection_fields:
        value = inventory.get(
            field
        )

        if isinstance(
            value,
            list,
        ):
            return sum(
                extract_sellable_quantity(
                    item
                )
                for item in value
            )

    available = inventory.get(
        "available"
    )

    if available is None:
        available = inventory.get(
            "quantity"
        )

    if available is None:
        available = inventory.get(
            "physical"
        )

    reserved = inventory.get(
        "reserved",
        0,
    )

    if isinstance(
        available,
        (int, float),
    ):
        if not isinstance(
            reserved,
            (int, float),
        ):
            reserved = 0

        return max(
            int(available)
            - int(reserved),
            0,
        )

    return 0


def build_inventory_response(
    result: dict,
) -> str:

    product = result[
        "product"
    ]

    inventory = result[
        "inventory"
    ]

    product_name = (
        product.get(
            "product_name"
        )
        or product.get(
            "name"
        )
        or "this product"
    )

    total_sellable = (
        extract_sellable_quantity(
            inventory
        )
    )

    return (
        f"There are {total_sellable} "
        f"sellable units of "
        f"{product_name}."
    )


def build_approval_list_response(
    approvals,
) -> str:

    if not approvals:
        return (
            "There are no pending "
            "approvals."
        )

    lines = [
        (
            f"There are "
            f"{len(approvals)} pending "
            f"approval(s):"
        )
    ]

    for approval in approvals:
        lines.append(
            f"- Thread "
            f"{approval.thread_id}"
        )

    return "\n".join(
        lines
    )


def handle_confirmation(
    db: Session,
    conversation,
    user: User,
) -> AgentChatResponse:

    thread_id = (
        conversation.pending_thread_id
    )

    if not thread_id:
        response_text = (
            "There isn't an action waiting "
            "for confirmation."
        )

        add_message(
            db=db,
            conversation=conversation,
            role="assistant",
            content=response_text,
        )

        return AgentChatResponse(
            conversation_id=(
                conversation.conversation_id
            ),
            message=response_text,
            selected_agent=(
                "conversation_action"
            ),
        )

    existing_approval = (
        db.query(Approval)
        .filter(
            Approval.thread_id
            == thread_id
        )
        .first()
    )

    if not existing_approval:
        approval = Approval(
            thread_id=thread_id,
            status="pending",
            requested_by_user_id=user.id,
        )

        db.add(
            approval
        )

        db.commit()

    clear_pending_action(
        db=db,
        conversation=conversation,
    )

    response_text = (
        "Done. I've submitted the quote "
        "for manager approval."
    )

    add_message(
        db=db,
        conversation=conversation,
        role="assistant",
        content=response_text,
        message_type=(
            "approval_submitted"
        ),
        workflow_thread_id=thread_id,
    )

    return AgentChatResponse(
        conversation_id=(
            conversation.conversation_id
        ),
        message=response_text,
        workflow_thread_id=thread_id,
        awaiting_confirmation=False,
        selected_agent=(
            "conversation_action"
        ),
        action=AgentAction(
            type="approval_submitted",
            data={
                "thread_id":
                    thread_id
            },
        ),
    )


def handle_rejection(
    db: Session,
    conversation,
) -> AgentChatResponse:

    thread_id = (
        conversation.pending_thread_id
    )

    clear_pending_action(
        db=db,
        conversation=conversation,
    )

    response_text = (
        "Okay. I won't submit the quote "
        "for approval."
    )

    add_message(
        db=db,
        conversation=conversation,
        role="assistant",
        content=response_text,
        workflow_thread_id=thread_id,
    )

    return AgentChatResponse(
        conversation_id=(
            conversation.conversation_id
        ),
        message=response_text,
        workflow_thread_id=thread_id,
        awaiting_confirmation=False,
        selected_agent=(
            "conversation_action"
        ),
    )


def handle_agent_message(
    request: AgentChatRequest,
    db: Session,
    user: User,
) -> AgentChatResponse:

    conversation = (
        get_or_create_conversation(
            db=db,
            conversation_id=(
                request.conversation_id
            ),
            user_id=user.id,
            username=user.username,
        )
    )

    add_message(
        db=db,
        conversation=conversation,
        role="user",
        content=request.message,
    )

    normalized_message = (
        request.message
        .strip()
        .lower()
    )

    
    
    

    if conversation.pending_action:

        if (
            normalized_message
            in YES_MESSAGES
        ):
            logger.info(
                (
                    "conversation=%s "
                    "selected_agent="
                    "conversation_action"
                ),
                conversation.conversation_id,
            )

            return handle_confirmation(
                db=db,
                conversation=conversation,
                user=user,
            )

        if (
            normalized_message
            in NO_MESSAGES
        ):
            logger.info(
                (
                    "conversation=%s "
                    "selected_agent="
                    "conversation_action"
                ),
                conversation.conversation_id,
            )

            return handle_rejection(
                db=db,
                conversation=conversation,
            )

    
    
    

    raw_intent = (
        parse_agent_intent(
            request.message
        )
    )

    context = (
        get_conversation_context(
            conversation
        )
    )

    intent = (
        resolve_intent_context(
            intent=raw_intent,
            context=context,
        )
    )

    selected_agent = (
        select_agent(
            intent
        )
    )

    logger.info(
        (
            "conversation=%s "
            "user=%s "
            "intent=%s "
            "selected_agent=%s"
        ),
        conversation.conversation_id,
        user.username,
        intent.intent,
        selected_agent,
    )

    
    
    

    if (
        selected_agent
        == "conversation_action"
    ):
        if (
            intent.intent
            == "confirm_action"
        ):
            return handle_confirmation(
                db=db,
                conversation=conversation,
                user=user,
            )

        return handle_rejection(
            db=db,
            conversation=conversation,
        )

    
    
    

    if (
        selected_agent
        == "inventory_agent"
    ):

        if not intent.product_name:
            response_text = (
                "Which product would you "
                "like me to check?"
            )

        else:
            result = (
                run_inventory_agent(
                    db=db,
                    product_name=(
                        intent.product_name
                    ),
                )
            )

            response_text = (
                build_inventory_response(
                    result
                )
            )

            update_conversation_context(
                db=db,
                conversation=conversation,
                product_name=(
                    intent.product_name
                ),
            )

        add_message(
            db=db,
            conversation=conversation,
            role="assistant",
            content=response_text,
        )

        return AgentChatResponse(
            conversation_id=(
                conversation.conversation_id
            ),
            message=response_text,
            selected_agent=(
                "inventory_agent"
            ),
        )

    
    
    

    if (
        selected_agent
        == "quote_agent"
    ):

        if not intent.customer_name:
            response_text = (
                "Which customer is this "
                "quote for?"
            )

            add_message(
                db=db,
                conversation=conversation,
                role="assistant",
                content=response_text,
            )

            return AgentChatResponse(
                conversation_id=(
                    conversation.conversation_id
                ),
                message=response_text,
                selected_agent=(
                    "quote_agent"
                ),
            )

        if not intent.product_name:
            response_text = (
                "Which product should I "
                "quote?"
            )

            add_message(
                db=db,
                conversation=conversation,
                role="assistant",
                content=response_text,
            )

            return AgentChatResponse(
                conversation_id=(
                    conversation.conversation_id
                ),
                message=response_text,
                selected_agent=(
                    "quote_agent"
                ),
            )

        if intent.quantity is None:
            response_text = (
                "How many units should I "
                "quote?"
            )

            add_message(
                db=db,
                conversation=conversation,
                role="assistant",
                content=response_text,
            )

            return AgentChatResponse(
                conversation_id=(
                    conversation.conversation_id
                ),
                message=response_text,
                selected_agent=(
                    "quote_agent"
                ),
            )

        result = run_quote_agent(
            db=db,
            user=user,
            message=request.message,
            intent=intent,
            idempotency_key=(
                request.idempotency_key
                or str(uuid4())
            ),
        )

        response_text = (
            build_quote_response(
                result
            )
        )

        update_conversation_context(
            db=db,
            conversation=conversation,
            customer_name=(
                intent.customer_name
            ),
            product_name=(
                intent.product_name
            ),
            quantity=(
                intent.quantity
            ),
        )

        awaiting_confirmation = (
            result.status
            == "awaiting_approval"
        )

        if awaiting_confirmation:
            set_pending_action(
                db=db,
                conversation=conversation,
                action=(
                    "submit_quote_approval"
                ),
                thread_id=(
                    result.thread_id
                ),
            )

        add_message(
            db=db,
            conversation=conversation,
            role="assistant",
            content=response_text,
            message_type="quote",
            workflow_thread_id=(
                result.thread_id
            ),
        )

        return AgentChatResponse(
            conversation_id=(
                conversation.conversation_id
            ),
            message=response_text,
            workflow_thread_id=(
                result.thread_id
            ),
            awaiting_confirmation=(
                awaiting_confirmation
            ),
            selected_agent=(
                "quote_agent"
            ),
            action=(
                AgentAction(
                    type=(
                        "confirm_approval"
                    ),
                    data={
                        "thread_id":
                            result.thread_id
                    },
                )
                if awaiting_confirmation
                else None
            ),
        )

    
    
    

    if (
        selected_agent
        == "approval_agent"
    ):

        if user.role not in {
            "manager",
            "admin",
        }:
            response_text = (
                "You don't have permission "
                "to view approval workflows."
            )

        elif (
            intent.intent
            == "list_approvals"
        ):
            approvals = (
                list_pending_approvals(
                    db
                )
            )

            response_text = (
                build_approval_list_response(
                    approvals
                )
            )

        else:
            response_text = (
                "I can currently list "
                "pending approvals. "
                "Approval execution through "
                "chat will be added next."
            )

        add_message(
            db=db,
            conversation=conversation,
            role="assistant",
            content=response_text,
        )

        return AgentChatResponse(
            conversation_id=(
                conversation.conversation_id
            ),
            message=response_text,
            selected_agent=(
                "approval_agent"
            ),
        )

    
    
    

    response_text = (
        run_general_agent()
    )

    add_message(
        db=db,
        conversation=conversation,
        role="assistant",
        content=response_text,
    )

    return AgentChatResponse(
        conversation_id=(
            conversation.conversation_id
        ),
        message=response_text,
        selected_agent=(
            "general_agent"
        ),
    )