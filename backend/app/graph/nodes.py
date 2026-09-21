from langgraph.types import interrupt

from app.core.database import SessionLocal
from app.core.exceptions import (
    ExternalServiceError,
    ModelResponseError,
)
from app.graph.error_handling import (
    build_failure_state,
)
from app.graph.observability import (
    record_node_event,
)
from app.graph.state import QuoteWorkflowState
from app.llm.bedrock import parse_quote_request
from app.monitoring.logger import logger
from app.schemas.quote import QuoteResponse
from app.services.ai_quote_service import (
    validate_parsed_quote_request,
)
from app.tools.customer_tools import (
    create_customer_lookup_tool,
)
from app.tools.inventory_tools import (
    create_inventory_lookup_tool,
)
from app.tools.pricing_tools import (
    create_pricing_lookup_tool,
)
from app.tools.product_tools import (
    create_product_lookup_tool,
)
from app.tools.quote_tools import (
    create_quote_tool,
)


def parse_request_node(
    state: QuoteWorkflowState,
) -> dict:

    logger.info(
        "Workflow started by user=%s role=%s",
        state.get("username"),
        state.get("user_role"),
    )

    logger.info(
        "LangGraph node: parse_request"
    )

    record_node_event(
        workflow_run_id=state.get(
            "workflow_run_id"
        ),
        node_name="parse_request",
        status="started",
    )

    try:
        parsed_request = parse_quote_request(
            state["message"],
            workflow_run_id=state.get(
                "workflow_run_id"
            ),
        )

        validate_parsed_quote_request(
            parsed_request
        )

        record_node_event(
            workflow_run_id=state.get(
                "workflow_run_id"
            ),
            node_name="parse_request",
            status="completed",
        )

        return {
            "parsed_request": parsed_request,
            "current_node": "parse_request",
        }

    except ExternalServiceError as exc:
        record_node_event(
            workflow_run_id=state.get(
                "workflow_run_id"
            ),
            node_name="parse_request",
            status="failed",
            message=str(exc),
        )

        return build_failure_state(
            exc=exc,
            node_name="parse_request",
            retry_count=2,
        )

    except ModelResponseError as exc:
        record_node_event(
            workflow_run_id=state.get(
                "workflow_run_id"
            ),
            node_name="parse_request",
            status="failed",
            message=str(exc),
        )

        return build_failure_state(
            exc=exc,
            node_name="parse_request",
            retry_count=0,
        )

    except ValueError as exc:
        record_node_event(
            workflow_run_id=state.get(
                "workflow_run_id"
            ),
            node_name="parse_request",
            status="failed",
            message=str(exc),
        )

        return build_failure_state(
            exc=exc,
            node_name="parse_request",
            retry_count=0,
        )


def resolve_customer_node(
    state: QuoteWorkflowState,
) -> dict:

    logger.info(
        "LangGraph node: resolve_customer"
    )

    record_node_event(
        workflow_run_id=state.get(
            "workflow_run_id"
        ),
        node_name="resolve_customer",
        status="started",
    )

    db = SessionLocal()

    try:
        customer_tool = (
            create_customer_lookup_tool(
                db
            )
        )

        customer_data = (
            customer_tool.invoke(
                {
                    "customer_name":
                        state[
                            "parsed_request"
                        ].customer_name
                }
            )
        )

        record_node_event(
            workflow_run_id=state.get(
                "workflow_run_id"
            ),
            node_name="resolve_customer",
            status="completed",
        )

        return {
            "customer_data":
                customer_data,
            "current_node":
                "resolve_customer",
        }

    except Exception as exc:
        record_node_event(
            workflow_run_id=state.get(
                "workflow_run_id"
            ),
            node_name="resolve_customer",
            status="failed",
            message=str(exc),
        )

        return build_failure_state(
            exc=exc,
            node_name="resolve_customer",
        )

    finally:
        db.close()


def resolve_product_node(
    state: QuoteWorkflowState,
) -> dict:

    logger.info(
        "LangGraph node: resolve_product"
    )

    record_node_event(
        workflow_run_id=state.get(
            "workflow_run_id"
        ),
        node_name="resolve_product",
        status="started",
    )

    db = SessionLocal()

    try:
        product_tool = (
            create_product_lookup_tool(
                db
            )
        )

        product_data = (
            product_tool.invoke(
                {
                    "product_name":
                        state[
                            "parsed_request"
                        ].product_name
                }
            )
        )

        record_node_event(
            workflow_run_id=state.get(
                "workflow_run_id"
            ),
            node_name="resolve_product",
            status="completed",
        )

        return {
            "product_data":
                product_data,
            "current_node":
                "resolve_product",
        }

    except Exception as exc:
        record_node_event(
            workflow_run_id=state.get(
                "workflow_run_id"
            ),
            node_name="resolve_product",
            status="failed",
            message=str(exc),
        )

        return build_failure_state(
            exc=exc,
            node_name="resolve_product",
        )

    finally:
        db.close()


def check_inventory_node(
    state: QuoteWorkflowState,
) -> dict:

    logger.info(
        "LangGraph node: check_inventory"
    )

    record_node_event(
        workflow_run_id=state.get(
            "workflow_run_id"
        ),
        node_name="check_inventory",
        status="started",
    )

    db = SessionLocal()

    try:
        inventory_tool = (
            create_inventory_lookup_tool(
                db
            )
        )

        inventory_data = (
            inventory_tool.invoke(
                {
                    "sku":
                        state[
                            "product_data"
                        ]["sku"]
                }
            )
        )

        record_node_event(
            workflow_run_id=state.get(
                "workflow_run_id"
            ),
            node_name="check_inventory",
            status="completed",
        )

        return {
            "inventory_data":
                inventory_data,
            "current_node":
                "check_inventory",
        }

    except Exception as exc:
        record_node_event(
            workflow_run_id=state.get(
                "workflow_run_id"
            ),
            node_name="check_inventory",
            status="failed",
            message=str(exc),
        )

        return build_failure_state(
            exc=exc,
            node_name="check_inventory",
        )

    finally:
        db.close()


def get_pricing_node(
    state: QuoteWorkflowState,
) -> dict:

    logger.info(
        "LangGraph node: get_pricing"
    )

    record_node_event(
        workflow_run_id=state.get(
            "workflow_run_id"
        ),
        node_name="get_pricing",
        status="started",
    )

    db = SessionLocal()

    try:
        pricing_tool = (
            create_pricing_lookup_tool(
                db
            )
        )

        pricing_data = (
            pricing_tool.invoke(
                {
                    "customer_code":
                        state[
                            "customer_data"
                        ][
                            "customer_code"
                        ],
                    "sku":
                        state[
                            "product_data"
                        ]["sku"],
                }
            )
        )

        record_node_event(
            workflow_run_id=state.get(
                "workflow_run_id"
            ),
            node_name="get_pricing",
            status="completed",
        )

        return {
            "pricing_data":
                pricing_data,
            "current_node":
                "get_pricing",
        }

    except Exception as exc:
        record_node_event(
            workflow_run_id=state.get(
                "workflow_run_id"
            ),
            node_name="get_pricing",
            status="failed",
            message=str(exc),
        )

        return build_failure_state(
            exc=exc,
            node_name="get_pricing",
        )

    finally:
        db.close()


def build_quote_node(
    state: QuoteWorkflowState,
) -> dict:

    logger.info(
        "LangGraph node: build_quote"
    )

    record_node_event(
        workflow_run_id=state.get(
            "workflow_run_id"
        ),
        node_name="build_quote",
        status="started",
    )

    db = SessionLocal()

    try:
        quote_tool = create_quote_tool(
            db
        )

        quote_data = quote_tool.invoke(
            {
                "customer_code":
                    state[
                        "customer_data"
                    ][
                        "customer_code"
                    ],
                "sku":
                    state[
                        "product_data"
                    ]["sku"],
                "quantity":
                    state[
                        "parsed_request"
                    ].quantity,
            }
        )

        quote = (
            QuoteResponse
            .model_validate(
                quote_data
            )
        )

        record_node_event(
            workflow_run_id=state.get(
                "workflow_run_id"
            ),
            node_name="build_quote",
            status="completed",
        )

        return {
            "quote": quote,
            "current_node":
                "build_quote",
        }

    except Exception as exc:
        record_node_event(
            workflow_run_id=state.get(
                "workflow_run_id"
            ),
            node_name="build_quote",
            status="failed",
            message=str(exc),
        )

        return build_failure_state(
            exc=exc,
            node_name="build_quote",
        )

    finally:
        db.close()


def evaluate_approval_node(
    state: QuoteWorkflowState,
) -> dict:

    logger.info(
        "LangGraph node: "
        "evaluate_approval"
    )

    record_node_event(
        workflow_run_id=state.get(
            "workflow_run_id"
        ),
        node_name="evaluate_approval",
        status="started",
    )

    quote = state["quote"]

    record_node_event(
        workflow_run_id=state.get(
            "workflow_run_id"
        ),
        node_name="evaluate_approval",
        status="completed",
    )

    return {
        "requires_approval":
            quote.requires_approval,
        "approval_reasons":
            quote.approval_reasons,
        "current_node":
            "evaluate_approval",
    }


def approved_path_node(
    state: QuoteWorkflowState,
) -> dict:

    logger.info(
        "LangGraph node: approved_path"
    )

    record_node_event(
        workflow_run_id=state.get(
            "workflow_run_id"
        ),
        node_name="approved_path",
        status="completed",
    )

    return {
        "current_node": "approved_path",
        "workflow_status": "ready",
    }


def approval_required_node(
    state: QuoteWorkflowState,
) -> dict:

    logger.info(
        "LangGraph node: "
        "approval_required"
    )

    quote = state["quote"]

    record_node_event(
        workflow_run_id=state.get(
            "workflow_run_id"
        ),
        node_name="approval_required",
        status="awaiting_approval",
        metadata={
            "approval_reasons":
                state.get(
                    "approval_reasons",
                    [],
                )
        },
    )

    decision = interrupt(
        {
            "type": "quote_approval",
            "message": (
                "This quote requires "
                "manager approval."
            ),
            "customer_code":
                quote.customer_code,
            "customer_name":
                quote.customer_name,
            "sku":
                quote.sku,
            "product_name":
                quote.product_name,
            "quantity_requested":
                quote.quantity_requested,
            "quantity_available":
                quote.quantity_available,
            "subtotal":
                str(
                    quote.subtotal
                ),
            "approval_reasons":
                quote.approval_reasons,
        }
    )

    return {
        "approval_decision":
            decision["decision"],
        "approved_by_user_id":
            decision["user_id"],
        "approved_by_username":
            decision["username"],
        "approval_comment":
            decision.get(
                "comment"
            ),
        "current_node":
            "approval_required",
    }


def approval_accepted_node(
    state: QuoteWorkflowState,
) -> dict:

    logger.info(
        "LangGraph node: "
        "approval_accepted"
    )

    record_node_event(
        workflow_run_id=state.get(
            "workflow_run_id"
        ),
        node_name="approval_accepted",
        status="completed",
        metadata={
            "approved_by":
                state.get(
                    "approved_by_username"
                )
        },
    )

    return {
        "workflow_status": "approved",
        "current_node":
            "approval_accepted",
    }


def approval_rejected_node(
    state: QuoteWorkflowState,
) -> dict:

    logger.info(
        "LangGraph node: "
        "approval_rejected"
    )

    record_node_event(
        workflow_run_id=state.get(
            "workflow_run_id"
        ),
        node_name="approval_rejected",
        status="completed",
        metadata={
            "decided_by":
                state.get(
                    "approved_by_username"
                )
        },
    )

    return {
        "workflow_status": "rejected",
        "current_node":
            "approval_rejected",
    }


def workflow_failed_node(
    state: QuoteWorkflowState,
) -> dict:

    logger.error(
        "LangGraph workflow failed "
        "node=%s type=%s message=%s",
        state.get(
            "failed_node"
        ),
        state.get(
            "error_type"
        ),
        state.get(
            "error_message"
        ),
    )

    record_node_event(
        workflow_run_id=state.get(
            "workflow_run_id"
        ),
        node_name="workflow_failed",
        status="failed",
        message=state.get(
            "error_message"
        ),
        metadata={
            "failed_node":
                state.get(
                    "failed_node"
                ),
            "error_type":
                state.get(
                    "error_type"
                ),
        },
    )

    return {
        "workflow_status": "failed",
        "current_node":
            "workflow_failed",
    }