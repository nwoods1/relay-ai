from langgraph.graph import StateGraph, START, END

from app.graph.state import QuoteWorkflowState
from app.graph.nodes import (
    parse_request_node,
    resolve_customer_node,
    resolve_product_node,
    build_quote_node,
    evaluate_approval_node,
    approved_path_node,
    approval_required_node,
)

def route_after_approval(
    state: QuoteWorkflowState,
) -> str:

    if state["requires_approval"]:
        return "approval_required"

    return "approved_path"

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

workflow.add_edge(
    "approval_required",
    END,
)

quote_workflow = workflow.compile()