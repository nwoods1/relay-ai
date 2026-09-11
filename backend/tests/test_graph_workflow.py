from unittest.mock import patch

from app.core.database import SessionLocal
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

    db = SessionLocal()

    try:
        result = quote_workflow.invoke(
            {
                "message": "Give me a quote",
                "db": db,
            }
        )

        assert result["quote"] is not None

        assert (
            result["quote"].customer_code
            == "BP-20001"
        )

        assert (
            result["quote"].sku
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

    finally:
        db.close()


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

    db = SessionLocal()

    try:
        result = quote_workflow.invoke(
            {
                "message": "Large order",
                "db": db,
            }
        )

        assert result["requires_approval"] is True

        assert (
            result["workflow_status"]
            == "awaiting_approval"
        )

        assert (
            result["inventory_data"]["total_available"]
            == 89
        )

        assert (
            result["pricing_data"]["pricing_tier"]
            == "B"
        )

    finally:
        db.close()