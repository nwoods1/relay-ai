from sqlalchemy.orm import Session

from app.graph.state import QuoteWorkflowState
from app.monitoring.logger import logger
from app.llm.bedrock import parse_quote_request
from app.services.ai_quote_service import (
    validate_parsed_quote_request,
)
from app.schemas.quote import QuoteResponse
from app.tools.customer_tools import (
    create_customer_lookup_tool,
)
from app.tools.product_tools import (
    create_product_lookup_tool,
)
from app.tools.quote_tools import (
    create_quote_tool,
)
from app.tools.inventory_tools import (
    create_inventory_lookup_tool,
)
from app.tools.pricing_tools import (
    create_pricing_lookup_tool,
)
from langgraph.types import interrupt
from app.core.database import SessionLocal


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

    parsed_request = parse_quote_request(
        message=state["message"]
    )

    validate_parsed_quote_request(
        parsed_request
    )

    return {
        "parsed_request": parsed_request,
        "current_node": "parse_request",
    }

def resolve_customer_node(
    state: QuoteWorkflowState,
) -> dict:

    logger.info(
        "LangGraph node: resolve_customer"
    )

    parsed_request = state["parsed_request"]

    db = SessionLocal()

    try:
        customer_tool = create_customer_lookup_tool(
            db
        )

        customer_data = customer_tool.invoke(
            {
                "customer_name":
                    parsed_request.customer_name
            }
        )

        return {
            "customer_data": customer_data,
            "current_node": "resolve_customer",
        }

    finally:
        db.close()

def resolve_product_node(
    state: QuoteWorkflowState,
) -> dict:

    logger.info(
        "LangGraph node: resolve_product"
    )

    parsed_request = state["parsed_request"]

    db = SessionLocal()

    try:
        product_tool = create_product_lookup_tool(
            db
        )

        product_data = product_tool.invoke(
            {
                "product_name":
                    parsed_request.product_name
            }
        )

        return {
            "product_data": product_data,
            "current_node": "resolve_product",
        }

    finally:
        db.close()

def build_quote_node(
    state: QuoteWorkflowState,
) -> dict:

    logger.info(
        "LangGraph node: build_quote"
    )

    parsed_request = state["parsed_request"]
    customer_data = state["customer_data"]
    product_data = state["product_data"]

    db = SessionLocal()

    try:
        quote_tool = create_quote_tool(
            db
        )

        quote_data = quote_tool.invoke(
            {
                "customer_code":
                    customer_data["customer_code"],
                "sku":
                    product_data["sku"],
                "quantity":
                    parsed_request.quantity,
            }
        )

        quote = QuoteResponse.model_validate(
            quote_data
        )

        return {
            "quote": quote,
            "current_node": "build_quote",
        }

    finally:
        db.close()

def evaluate_approval_node(
    state: QuoteWorkflowState,
) -> dict:

    logger.info(
        "LangGraph node: evaluate_approval"
    )

    quote = state["quote"]

    return {
        "requires_approval": quote.requires_approval,
        "approval_reasons": quote.approval_reasons,
        "current_node": "evaluate_approval",
    }

def approved_path_node(
    state: QuoteWorkflowState,
) -> dict:

    return {
        "current_node": "approved_path",
        "workflow_status": "ready",
    }


def approval_required_node(
    state: QuoteWorkflowState,
) -> dict:

    logger.info(
        "LangGraph node: approval_required"
    )

    quote = state["quote"]

    decision = interrupt(
        {
            "type": "quote_approval",
            "message": "This quote requires manager approval.",
            "customer_code": quote.customer_code,
            "customer_name": quote.customer_name,
            "sku": quote.sku,
            "product_name": quote.product_name,
            "quantity_requested": quote.quantity_requested,
            "quantity_available": quote.quantity_available,
            "subtotal": str(quote.subtotal),
            "approval_reasons": quote.approval_reasons,
        }
    )

    return {
        "approval_decision": decision["decision"],
        "approved_by_user_id": decision["user_id"],
        "approved_by_username": decision["username"],
        "approval_comment": decision.get("comment"),
        "current_node": "approval_required",
    }

def check_inventory_node(
    state: QuoteWorkflowState,
) -> dict:

    logger.info(
        "LangGraph node: check_inventory"
    )

    db = SessionLocal()

    try:
        inventory_tool = (
            create_inventory_lookup_tool(db)
        )

        inventory_data = inventory_tool.invoke(
            {
                "sku":
                    state["product_data"]["sku"]
            }
        )

        return {
            "inventory_data": inventory_data,
            "current_node": "check_inventory",
        }

    finally:
        db.close()

def get_pricing_node(
    state: QuoteWorkflowState,
) -> dict:

    logger.info(
        "LangGraph node: get_pricing"
    )

    db = SessionLocal()

    try:
        pricing_tool = (
            create_pricing_lookup_tool(db)
        )

        pricing_data = pricing_tool.invoke(
            {
                "customer_code":
                    state["customer_data"][
                        "customer_code"
                    ],
                "sku":
                    state["product_data"]["sku"],
            }
        )

        return {
            "pricing_data": pricing_data,
            "current_node": "get_pricing",
        }

    finally:
        db.close()

def approval_accepted_node(
    state: QuoteWorkflowState,
) -> dict:

    logger.info(
        "LangGraph node: approval_accepted"
    )

    return {
        "workflow_status": "approved",
        "current_node": "approval_accepted",
    }


def approval_rejected_node(
    state: QuoteWorkflowState,
) -> dict:

    logger.info(
        "LangGraph node: approval_rejected"
    )

    return {
        "workflow_status": "rejected",
        "current_node": "approval_rejected",
    }