from unittest.mock import patch
from uuid import uuid4

from app.graph.workflow import quote_workflow
from app.schemas.ai import ParsedQuoteRequest


@patch(
    "app.graph.nodes.parse_quote_request"
)
def test_graph_runs_quote_workflow(
    mock_parse_quote_request,
):
    mock_parse_quote_request.return_value = (
        ParsedQuoteRequest(
            customer_name="Pacific Mountain Outfitters",
            product_name="Alpine Shell Jacket",
            quantity=1,
        )
    )

    thread_id = str(uuid4())

    result = quote_workflow.invoke(
        {
            "message": "Give me a quote",
            "user_id": 1,
            "username": "sales",
            "user_role": "sales_rep",
        },
        config={
            "configurable": {
                "thread_id": thread_id
            }
        },
    )

    assert (
        result["parsed_request"].customer_name
        == "Pacific Mountain Outfitters"
    )

    assert (
        result["parsed_request"].product_name
        == "Alpine Shell Jacket"
    )

    assert (
        result["parsed_request"].quantity
        == 1
    )

    assert (
        result["customer_data"]["customer_code"]
        == "BP-20001"
    )

    assert (
        result["product_data"]["sku"]
        == "JACKET-BETA-AR-M"
    )

    assert (
        result["inventory_data"]["total_available"]
        == 89
    )

    assert (
        result["pricing_data"]["pricing_tier"]
        == "B"
    )

    assert (
        result["quote"].quantity_requested
        == 1
    )

    assert (
        result["quote"].fulfillment_status
        == "available"
    )

    assert (
        result["requires_approval"]
        is False
    )

    assert (
        result["workflow_status"]
        == "ready"
    )


@patch(
    "app.graph.nodes.parse_quote_request"
)
def test_graph_routes_to_approval(
    mock_parse_quote_request,
):
    mock_parse_quote_request.return_value = (
        ParsedQuoteRequest(
            customer_name="Pacific Mountain Outfitters",
            product_name="Alpine Shell Jacket",
            quantity=500,
        )
    )

    thread_id = str(uuid4())

    result = quote_workflow.invoke(
        {
            "message": "Give me a quote",
            "user_id": 1,
            "username": "sales",
            "user_role": "sales_rep",
        },
        config={
            "configurable": {
                "thread_id": thread_id
            }
        },
    )

    assert (
        result["inventory_data"]["total_available"]
        == 89
    )

    assert (
        result["pricing_data"]["pricing_tier"]
        == "B"
    )

    assert (
        result["quote"].quantity_requested
        == 500
    )

    assert (
        result["quote"].fulfillment_status
        == "partial"
    )

    assert (
        result["requires_approval"]
        is True
    )

    assert (
        "Requested quantity cannot be fully fulfilled"
        in result["approval_reasons"]
    )

    assert "__interrupt__" in result

    assert result["__interrupt__"]