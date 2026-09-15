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
    workflow_failed_node,
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

def route_after_node(
    state: QuoteWorkflowState,
) -> str:

    if (
        state.get("workflow_status")
        == "failed"
    ):
        return "failed"

    return "continue"


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

workflow.add_node(
    "workflow_failed",
    workflow_failed_node,
)

workflow.add_edge(
    START,
    "parse_request",
)

workflow.add_conditional_edges(
    "parse_request",
    route_after_node,
    {
        "continue": "resolve_customer",
        "failed": "workflow_failed",
    },
)

workflow.add_conditional_edges(
    "resolve_customer",
    route_after_node,
    {
        "continue": "resolve_product",
        "failed": "workflow_failed",
    },
)

workflow.add_conditional_edges(
    "resolve_product",
    route_after_node,
    {
        "continue": "check_inventory",
        "failed": "workflow_failed",
    },
)

workflow.add_conditional_edges(
    "check_inventory",
    route_after_node,
    {
        "continue": "get_pricing",
        "failed": "workflow_failed",
    },
)

workflow.add_conditional_edges(
    "get_pricing",
    route_after_node,
    {
        "continue": "build_quote",
        "failed": "workflow_failed",
    },
)

workflow.add_conditional_edges(
    "build_quote",
    route_after_node,
    {
        "continue": "evaluate_approval",
        "failed": "workflow_failed",
    },
)

workflow.add_conditional_edges(
    "evaluate_approval",
    route_after_approval,
    {
        "approved_path": "approved_path",
        "approval_required": "approval_required",
    },
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
    "approved_path",
    END,
)

workflow.add_edge(
    "approval_accepted",
    END,
)

workflow.add_edge(
    "approval_rejected",
    END,
)

workflow.add_edge(
    "workflow_failed",
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

