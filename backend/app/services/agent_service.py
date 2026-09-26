import logging
from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.agents.approval_agent import (
    approve_pending_approval,
    get_approval_by_thread,
    list_pending_approvals,
    reject_pending_approval,
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
from app.guardrails.policy import (
    can_perform_action,
)
from app.guardrails.prompt_injection import (
    check_prompt_injection,
)
from app.guardrails.tool_validation import (
    validate_inventory_request,
    validate_quote_request,
)
from app.llm.agent_router import (
    parse_agent_intent,
)
from app.models.approval import Approval
from app.models.user import User
from app.schemas.agent import (
    AgentAction,
    AgentChatRequest,
    AgentChatResponse,
)
from app.services.agent_context_service import (
    build_router_input,
    clear_approval_context,
    get_conversation_context,
    record_conversation_action,
    resolve_intent_context,
    update_approval_context,
    update_conversation_context,
)
from app.services.conversation_service import (
    add_message,
    clear_pending_action,
    get_or_create_conversation,
    set_pending_action,
)


logger = logging.getLogger(
    "relay-ai"
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


def log_guardrail_block(
    conversation,
    user: User,
    category: str,
    reason: str,
) -> None:

    logger.warning(
        (
            "guardrail_blocked "
            "conversation=%s "
            "user_id=%s "
            "username=%s "
            "role=%s "
            "category=%s "
            "reason=%s"
        ),
        conversation.conversation_id,
        user.id,
        user.username,
        user.role,
        category,
        reason,
    )


def guardrail_response(
    db: Session,
    conversation,
    user: User,
    message: str,
    category: str,
    reason: str,
) -> AgentChatResponse:

    log_guardrail_block(
        conversation=conversation,
        user=user,
        category=category,
        reason=reason,
    )

    add_message(
        db=db,
        conversation=conversation,
        role="assistant",
        content=message,
        message_type="guardrail",
    )

    return AgentChatResponse(
        conversation_id=(
            conversation.conversation_id
        ),
        message=message,
        selected_agent="guardrail",
    )


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
            "There are no pending approvals."
        )

    if len(approvals) == 1:
        heading = (
            "There is 1 pending approval:"
        )
    else:
        heading = (
            f"There are {len(approvals)} "
            "pending approvals:"
        )

    lines = [
        heading,
        "",
    ]

    for index, approval in enumerate(
        approvals,
        start=1,
    ):
        lines.append(
            f"{index}. Approval request"
        )

        lines.append(
            f"   Thread: "
            f"{approval.thread_id}"
        )

        lines.append("")

    return "\n".join(
        lines
    ).strip()


def handle_confirmation(
    db: Session,
    conversation,
    user: User,
) -> AgentChatResponse:

    if not can_perform_action(
        user_role=user.role,
        action=(
            "submit_quote_approval"
        ),
    ):
        return guardrail_response(
            db=db,
            conversation=conversation,
            user=user,
            message=(
                "You don't have permission "
                "to perform that action."
            ),
            category=(
                "unauthorized_action"
            ),
            reason=(
                "The user's role does not "
                "have permission to submit "
                "a quote approval request."
            ),
        )

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
            requested_by_user_id=(
                user.id
            ),
        )

        db.add(
            approval
        )

        db.commit()

    clear_pending_action(
        db=db,
        conversation=conversation,
        action=(
        "submitted_for_approval"
        ),
        details={
            "thread_id":
                thread_id
        },
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
        workflow_thread_id=(
            thread_id
        ),
    )

    return AgentChatResponse(
        conversation_id=(
            conversation.conversation_id
        ),
        message=response_text,
        workflow_thread_id=(
            thread_id
        ),
        awaiting_confirmation=False,
        selected_agent=(
            "conversation_action"
        ),
        action=AgentAction(
            type=(
                "approval_submitted"
            ),
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
        action=(
            "approval_submission_cancelled"
        ),
        details={
            "thread_id":
                thread_id
        },
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
        workflow_thread_id=(
            thread_id
        ),
    )

    return AgentChatResponse(
        conversation_id=(
            conversation.conversation_id
        ),
        message=response_text,
        workflow_thread_id=(
            thread_id
        ),
        awaiting_confirmation=False,
        selected_agent=(
            "conversation_action"
        ),
    )


def resolve_approval_thread(
    db: Session,
    conversation,
    intent,
) -> tuple[
    str | None,
    str | None,
]:

    # Explicit thread ID from user.
    if intent.approval_thread_id:
        approval = get_approval_by_thread(
            db=db,
            thread_id=(
                intent.approval_thread_id
            ),
        )

        if approval is None:
            return (
                None,
                (
                    "I couldn't find an "
                    "approval with that "
                    "thread ID."
                ),
            )

        if approval.status != "pending":
            return (
                None,
                (
                    "That approval has "
                    "already been decided."
                ),
            )

        return (
            approval.thread_id,
            None,
        )

    # Approval remembered from this
    # conversation.
    if (
        conversation.last_approval_thread_id
    ):
        approval = get_approval_by_thread(
            db=db,
            thread_id=(
                conversation
                .last_approval_thread_id
            ),
        )

        if (
            approval is not None
            and approval.status
            == "pending"
        ):
            return (
                approval.thread_id,
                None,
            )

    # If no context exists, one pending
    # approval can be resolved safely.
    pending = list_pending_approvals(
        db
    )

    if len(pending) == 0:
        return (
            None,
            (
                "There are no pending "
                "approvals to act on."
            ),
        )

    # Never guess when multiple approvals
    # exist.
    if len(pending) > 1:
        return (
            None,
            (
                "There are multiple pending "
                "approvals. Please tell me "
                "which one you want to "
                "approve or reject."
            ),
        )

    return (
        pending[0].thread_id,
        None,
    )


def handle_approval_decision(
    db: Session,
    conversation,
    user: User,
    intent,
    idempotency_key: str | None = None,
) -> AgentChatResponse:

    is_approval = (
        intent.intent
        == "approve_quote"
    )

    action = (
        "approve_quote"
        if is_approval
        else "reject_quote"
    )

    # Defense in depth.
    # Authorization is also checked in the
    # main agent pipeline.
    if not can_perform_action(
        user_role=user.role,
        action=action,
    ):
        return guardrail_response(
            db=db,
            conversation=conversation,
            user=user,
            message=(
                "You don't have permission "
                "to perform that action."
            ),
            category=(
                "unauthorized_action"
            ),
            reason=(
                f"Role {user.role} cannot "
                f"perform {action}."
            ),
        )

    (
        thread_id,
        resolution_error,
    ) = resolve_approval_thread(
        db=db,
        conversation=conversation,
        intent=intent,
    )

    if resolution_error:
        add_message(
            db=db,
            conversation=conversation,
            role="assistant",
            content=resolution_error,
        )

        return AgentChatResponse(
            conversation_id=(
                conversation.conversation_id
            ),
            message=resolution_error,
            selected_agent=(
                "approval_agent"
            ),
        )

    approval = get_approval_by_thread(
        db=db,
        thread_id=thread_id,
    )

    if approval is None:
        response_text = (
            "I couldn't find that "
            "approval request."
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

    if approval.status != "pending":
        response_text = (
            "That approval has already "
            "been decided."
        )

        clear_approval_context(
            db=db,
            conversation=conversation,
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

    try:
        if is_approval:
            result = (
                approve_pending_approval(
                    db=db,
                    thread_id=thread_id,
                    user=user,
                    comment=(
                        intent.approval_comment
                    ),
                    idempotency_key=(
                        idempotency_key
                    ),
                )
            )

            response_text = (
                "Approved. The quote "
                "workflow has resumed "
                "successfully."
            )

            final_action = (
                "approved"
            )

        else:
            result = (
                reject_pending_approval(
                    db=db,
                    thread_id=thread_id,
                    user=user,
                    comment=(
                        intent.approval_comment
                    ),
                    idempotency_key=(
                        idempotency_key
                    ),
                )
            )

            response_text = (
                "Rejected. The quote "
                "workflow has been closed."
            )

            final_action = (
                "rejected"
            )

    except HTTPException as exc:

        if exc.status_code == 404:
            response_text = (
                "I couldn't find that "
                "approval request."
            )

        elif exc.status_code == 409:
            response_text = (
                "That approval has already "
                "been decided."
            )

            clear_approval_context(
                db=db,
                conversation=conversation,
            )

        else:
            raise

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

    # Once acted upon, do not allow
    # "approve it" to point to the same
    # approval again.
    clear_approval_context(
        db=db,
        conversation=conversation,
        action=final_action,
    )

    add_message(
        db=db,
        conversation=conversation,
        role="assistant",
        content=response_text,
        message_type=(
            "approval_decision"
        ),
        workflow_thread_id=(
            thread_id
        ),
    )

    return AgentChatResponse(
        conversation_id=(
            conversation.conversation_id
        ),
        message=response_text,
        workflow_thread_id=(
            thread_id
        ),
        awaiting_confirmation=False,
        selected_agent=(
            "approval_agent"
        ),
        action=AgentAction(
            type=final_action,
            data={
                "thread_id":
                    thread_id,
                "comment":
                    intent.approval_comment,
                "workflow_status":
                    result.status,
            },
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

    # ----------------------------------
    # Phase 13:
    # prompt-injection guardrail before
    # the LLM router.
    # ----------------------------------

    injection_result = (
        check_prompt_injection(
            request.message
        )
    )

    if not injection_result.allowed:
        return guardrail_response(
            db=db,
            conversation=conversation,
            user=user,
            message=(
                "I can't override Relay's "
                "system instructions, "
                "permissions, or approval "
                "requirements."
            ),
            category=(
                injection_result.category
                or "prompt_injection"
            ),
            reason=(
                injection_result.reason
                or "Prompt injection blocked."
            ),
        )

    normalized_message = (
        request.message
        .strip()
        .lower()
    )

    # ----------------------------------
    # Pending sales-side confirmation
    # ----------------------------------

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

    # ----------------------------------
    # Intent routing
    # ----------------------------------

    context = (
        get_conversation_context(
            conversation
        )
    )

    routing_input = (
        build_router_input(
            context=context,
            user_message=(
                request.message
            ),
        )
    )

    raw_intent = (
        parse_agent_intent(
            routing_input
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

    # ----------------------------------
    # Central authorization
    # ----------------------------------

    if not can_perform_action(
        user_role=user.role,
        action=intent.intent,
    ):
        return guardrail_response(
            db=db,
            conversation=conversation,
            user=user,
            message=(
                "You don't have permission "
                "to perform that action."
            ),
            category=(
                "unauthorized_action"
            ),
            reason=(
                f"Role {user.role} cannot "
                f"perform action "
                f"{intent.intent}."
            ),
        )

    # ----------------------------------
    # Conversation action
    # ----------------------------------

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

    # ----------------------------------
    # Inventory agent
    # ----------------------------------

    if (
        selected_agent
        == "inventory_agent"
    ):

        validation = (
            validate_inventory_request(
                intent.product_name
            )
        )

        if not validation.allowed:
            response_text = (
                "Which product would you "
                "like me to check?"
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

        try:
            result = (
                run_inventory_agent(
                    db=db,
                    product_name=(
                        intent.product_name
                    ),
                )
            )

        except HTTPException as exc:

            if exc.status_code == 404:
                response_text = (
                    "I couldn't find that "
                    "product in the current "
                    "catalog."
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

            raise

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
            warehouse_name=(
                intent.warehouse_name
            ),
            action="check_inventory",
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

    # ----------------------------------
    # Quote agent
    # ----------------------------------

    if (
        selected_agent
        == "quote_agent"
    ):

        validation = (
            validate_quote_request(
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
        )

        if not validation.allowed:

            if not intent.customer_name:
                response_text = (
                    "Which customer is this "
                    "quote for?"
                )

            elif not intent.product_name:
                response_text = (
                    "Which product should I "
                    "quote?"
                )

            elif intent.quantity is None:
                response_text = (
                    "How many units should I "
                    "quote?"
                )

            else:
                response_text = (
                    "I need a valid customer, "
                    "product, and quantity "
                    "before I can create "
                    "that quote."
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

        try:
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

        except HTTPException as exc:

            if exc.status_code == 404:
                response_text = (
                    "I couldn't find the "
                    "customer or product "
                    "needed for that quote."
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

            raise

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
            warehouse_name=(
                intent.warehouse_name
            ),
            action="create_quote",
            action_details={
                "thread_id":
                    result.thread_id,
                "status":
                    result.status,
            },
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

    # ----------------------------------
    # Approval agent
    # ----------------------------------

    if (
        selected_agent
        == "approval_agent"
    ):

        # Manager/admin wants to make
        # a decision.
        if (
            intent.intent
            in {
                "approve_quote",
                "reject_quote",
            }
        ):
            return handle_approval_decision(
                db=db,
                conversation=conversation,
                user=user,
                intent=intent,
                idempotency_key=(
                    request.idempotency_key
                ),
            )

        # Manager/admin wants to list
        # pending approvals.
        if (
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

            # When exactly one approval is
            # shown, remember it so that
            # "approve it" / "reject it"
            # works on the next turn.
            if len(approvals) == 1:
                update_approval_context(
                    db=db,
                    conversation=conversation,
                    thread_id=(
                        approvals[0]
                        .thread_id
                    ),
                    action="listed",
                )

            # Multiple approvals are
            # intentionally ambiguous.
            else:
                clear_approval_context(
                    db=db,
                    conversation=conversation,
                    action="listed",
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

    # ----------------------------------
    # General agent
    # ----------------------------------

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