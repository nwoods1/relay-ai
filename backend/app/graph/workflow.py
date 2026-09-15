from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.postgres import PostgresSaver
from psycopg import Connection

from app.core.config import settings
from app.graph.state import QuoteWorkflowState
from app.graph.nodes import (
    parse_request_node,
    resolve_customer_node,
    resolve_product_node,
    check_inventory_node,
    get_pricing_node,
    build_quote_node,
    evaluate_approval_node,
    approved_path_node,
    approval_required_node,
    approval_accepted_node,
    approval_rejected_node,
)


def route_after_approval(
    state: QuoteWorkflowState,
) -> str:

    if state["requires_approval"]:
        return "approval_required"

    return "approved_path"

def route_after_human_decision(
    state: QuoteWorkflowState,
) -> str:

    if state["approval_decision"] == "approved":
        return "approval_accepted"

    return "approval_rejected"


workflow = StateGraph(
    QuoteWorkflowState
)

workflow.add_node(
    "parse_request",
    parse_request_node,
)

workflow.add_node(
    "resolve_customer",
    resolve_customer_node,
)

workflow.add_node(
    "resolve_product",
    resolve_product_node,
)

workflow.add_node(
    "check_inventory",
    check_inventory_node,
)

workflow.add_node(
    "get_pricing",
    get_pricing_node,
)

workflow.add_node(
    "build_quote",
    build_quote_node,
)

workflow.add_node(
    "evaluate_approval",
    evaluate_approval_node,
)

workflow.add_node(
    "approved_path",
    approved_path_node,
)

workflow.add_node(
    "approval_required",
    approval_required_node,
)

workflow.add_node(
    "approval_accepted",
    approval_accepted_node,
)

workflow.add_node(
    "approval_rejected",
    approval_rejected_node,
)

workflow.add_edge(
    START,
    "parse_request",
)

workflow.add_edge(
    "parse_request",
    "resolve_customer",
)

workflow.add_edge(
    "resolve_customer",
    "resolve_product",
)

workflow.add_edge(
    "resolve_product",
    "check_inventory",
)

workflow.add_edge(
    "check_inventory",
    "get_pricing",
)

workflow.add_edge(
    "get_pricing",
    "build_quote",
)

workflow.add_edge(
    "build_quote",
    "evaluate_approval",
)

workflow.add_conditional_edges(
    "evaluate_approval",
    route_after_approval,
    {
        "approved_path": "approved_path",
        "approval_required": "approval_required",
    },
)

workflow.add_edge(
    "approved_path",
    END,
)

workflow.add_conditional_edges(
    "approval_required",
    route_after_human_decision,
    {
        "approval_accepted": "approval_accepted",
        "approval_rejected": "approval_rejected",
    },
)

workflow.add_edge(
    "approval_accepted",
    END,
)

workflow.add_edge(
    "approval_rejected",
    END,
)


postgres_connection = Connection.connect(
    settings.langgraph_database_url,
    autocommit=True,
    prepare_threshold=0,
)

checkpointer = PostgresSaver(
    postgres_connection
)

checkpointer.setup()

quote_workflow = workflow.compile(
    checkpointer=checkpointer
)

