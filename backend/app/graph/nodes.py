from sqlalchemy.orm import Session

from app.graph.state import QuoteWorkflowState
from app.monitoring.logger import logger
from app.llm.bedrock import parse_quote_request
from app.services.ai_quote_service import (
    validate_parsed_quote_request,
)
from app.services.entity_resolution_service import (
    resolve_customer,
    resolve_product,
)
from app.schemas.quote import QuoteRequest
from app.services.quote_service import create_quote


def parse_request_node(
    state: QuoteWorkflowState,
) -> dict:

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

    customer = resolve_customer(
        customer_name=parsed_request.customer_name,
        db=state["db"],
    )

    return {
        "customer": customer,
        "current_node": "resolve_customer",
    }

def resolve_product_node(
    state: QuoteWorkflowState,
) -> dict:

    logger.info(
        "LangGraph node: resolve_product"
    )

    parsed_request = state["parsed_request"]

    product = resolve_product(
        product_name=parsed_request.product_name,
        db=state["db"],
    )

    return {
        "product": product,
        "current_node": "resolve_product",
    }

def build_quote_node(
    state: QuoteWorkflowState,
) -> dict:

    logger.info(
        "LangGraph node: build_quote"
    )

    parsed_request = state["parsed_request"]
    customer = state["customer"]
    product = state["product"]

    quote_request = QuoteRequest(
        customer_code=customer.customer_code,
        sku=product.sku,
        quantity=parsed_request.quantity,
    )

    quote = create_quote(
        quote_request=quote_request,
        db=state["db"],
    )

    return {
        "quote": quote,
        "current_node": "build_quote",
    }

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

    return {
        "current_node": "approval_required",
        "workflow_status": "awaiting_approval",
    }